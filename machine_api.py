# machine_api.py
from fastapi import FastAPI, Response
from typing import Any, Dict,Literal
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import sys
import json
import uvicorn
import os

from Compression import Compression
from SerialDevice import SerialDevice
from MachineInterface import MachineInterface
import socket

# ---- Data models ----
class DeviceProfile(BaseModel):
    name: str
    execCommand: str
    description: str
    comType: Literal["usb", "ethernet"]

class NucModel(BaseModel):
    name: str
    description: str
    devices: Dict[str, Dict[str, str]]

# ---- Profile handling ----
if len(sys.argv) < 2:
    print("Usage: python3 machine_api.py <profile>. Using default 'compression'")
    # sys.exit(1)

machines: list[MachineInterface] = []

def buildmachines():
    machines.clear()

    for dev in app.state.nuc_model.devices:
        if devices[dev].comType == "usb":
            try:
                machine = SerialDevice(
                    device_id=dev,
                    execCommand=devices[dev].execCommand,
                    comAddress=app.state.nuc_model.devices[dev]['comAddress'],
                    name=devices[dev].name
                )
                machines.append(machine)

                print(f"Serial device {machine.name} connected on {machine.comPort}")
            except Exception as e:
                print(f"[WARN] Could not open serial port: {e}")
        elif devices[dev].comType == "ethernet":
            machine: Optional[MachineInterface] = None
            if(dev == "CompressionBench01"):
                print("Setting up compression bench:", dev)
                machine = Compression(
                    api_url=f"http://localhost:8001/jsonrpc",
                    api_key="CHANGE-ME-SOON",
                    device_id=dev,
                    execCommand=devices[dev].execCommand,
                    name=devices[dev].name,
                    comAddress=app.state.nuc_model.devices[dev]['comAddress']
                )
                machines.append(machine)
        else:
            print(f"[WARN] Unknown communication port for device {dev}")

    print("Initialized machines:", machines)
    for machine in machines:
        print(f"Machine {machine.device_id} - {machine.name} at {machine.comAddress}")

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate the structure of the config.json file."""
    REQUIRED_DEVICE_FIELDS = ["comAddress", "name", "description", "comType", "execCommand"]
    if "name" not in config or "description" not in config:
        print("[ERROR] Config missing top-level 'name' or 'description'")
        return False

    if "devices" not in config or not isinstance(config["devices"], dict):
        print("[ERROR] Config missing 'devices' dictionary")
        return False

    for dev_id, dev in config["devices"].items():
        for field in REQUIRED_DEVICE_FIELDS:
            if field not in dev:
                print(f"[ERROR] Device '{dev_id}' missing required field '{field}'")
                return False

        # Extra check: ensure comType is valid
        if dev["comType"] not in ("usb", "ethernet"):
            print(f"[ERROR] Device '{dev_id}' has invalid comType '{dev['comType']}'")
            return False

    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... initializing devices")
    if not validate_config(app.state.nuc_model):
        print("[FATAL] Invalid configuration. Exiting.")
        
    buildmachines()
    
    # hand over control to FastAPI
    yield

    # ---- Shutdown cleanup ----
    print("Shutting down... closing connections")

# ---- FastAPI app ----
app = FastAPI(title="Machine Controller API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load profiles from devices.json
with open("devices.json", "r") as f:
    raw_devices = json.load(f)
    devices = {name: DeviceProfile(**profile) for name, profile in raw_devices.items()}
    print("DEVICES: ", devices)
    
with open("nucs.json", "r") as f:
    nucs = json.load(f)

    app.state.nuc_model = NucModel(
        name=nucs["name"],
        description=nucs["description"],
        devices=nucs["devices"]
    )
    print("NUC: ", app.state.nuc_model)


@app.get("/devices")
def get_devices():
    return devices

@app.get("/config")
def get_config():
    return app.state.nuc_model.model_dump()

@app.post("/config")
def update_config(config: NucModel):
    if not validate_config(config.model_dump()):
        return Response(content=json.dumps({"error": "Invalid configuration"}), status_code=422, media_type="application/json")
    app.state.nuc_model = config
    with open("nucs.json", "w") as f:
        json.dump(config.model_dump(), f, indent=4)
    buildmachines()

    print("Updated configuration:", app.state.nuc_model)
    return {"Configuration updated"}

@app.get("/status")
def get_status():
    nuc_model = app.state.nuc_model
    if not validate_config(nuc_model.model_dump()):
        return {"error": "Invalid configuration"}
    
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.1.1", 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "Not found"

    return {
        "profile": nuc_model.name,
        "description": nuc_model.description,
        "ip_address": get_local_ip(),
        "machines": [
            {
                "device_id": machine.device_id,
                "name": machine.name,
                "comAddress": machine.comAddress,
                "connected": machine.get_status()
            }
            for machine in machines
        ]
    }

@app.get("/read/{device}")
async def read(device: str):
    print(machines)
    machine = next((machine for machine in machines if machine.device_id == device), None)
    if machine is None:
        return {"error": f"Device {device} not found"}
    
    print(f"Executing for {machine.device_id}")

    try:
        value = machine.get_data()
    except Exception as e:
        return Response(content=json.dumps({"error": f"Compression client error: {str(e)}"}), status_code=409, media_type="application/json")
    print("Data:", value)

    return value


# ---- Entry point ----
if __name__ == "__main__":
    uvicorn.run("machine_api:app", host="0.0.0.0", port=8000, reload=True)
