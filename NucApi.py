from fastapi import FastAPI, Response
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from contextlib import asynccontextmanager
from starlette.concurrency import run_in_threadpool
from dotenv import load_dotenv
from pathlib import Path
import contextlib
import os
import json
import uvicorn
import asyncio
import socket

from CompressionAdapter import CompressionAdapter
from NebestApi import get_config_from_api, load_machines, get_config_from_local, save_config_to_local
from Models import Machine, MachineAdapterType
from Parsers import caliperParser, scaleParser
from SerialPortHandler import SerialPortHandler
from Models import MachineAdapter

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

<<<<<<< HEAD
=======
config_location = "Not loaded"

>>>>>>> 63632f9753caa8cd2aa6bc555b31e5748d31b87f
nucId = os.getenv("NUCID", "0")
NEBESTSERVERURL = os.getenv("NEBESTSERVERURL", "acc2-inspectie.nebest.nl")
machinesAdapters: list[MachineAdapter] = []

def buildmachines(machines: dict[int, Machine]):
    """
    Initialize machine adapters based on the provided machine configurations.
    """
    machinesAdapters.clear()
    for dev in machines:
        if machines[dev].comType == MachineAdapterType.SERIAL:
            machine = SerialPortHandler(
                device_id=dev,
                comAddress=machines[dev].comAddress,
                name=machines[dev].name,
            )
            machinesAdapters.append(machine)
        elif machines[dev].comType == MachineAdapterType.SCALE:
            print("Setting up scale:", dev)
            machine = SerialPortHandler(
                device_id=dev,
                comAddress=machines[dev].comAddress,
                name=machines[dev].name,
                parser=scaleParser
            )
            machinesAdapters.append(machine)
        elif machines[dev].comType == MachineAdapterType.CALIPER:
            print("Setting up caliper:", dev)
            machine = SerialPortHandler(
                device_id=dev,
                comAddress=machines[dev].comAddress,
                name=machines[dev].name,
                parser=caliperParser
            )
            machinesAdapters.append(machine)
        elif machines[dev].comType == MachineAdapterType.COMPRESSION:
            print("Setting up compression bench:", dev)
            machine = CompressionAdapter(
                device_id=dev,
                name=machines[dev].name,
                comAddress=machines[dev].comAddress
            )
            machinesAdapters.append(machine)
        else:
            print(f"[WARN] Unknown adapter type for device {dev}")
            
    print("Initialized machines:", machinesAdapters)
    for machine in machinesAdapters:
        print(f"Machine {machine.device_id} - {machine.name} at {machine.comAddress}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager to initialize and clean up resources.
    """
<<<<<<< HEAD
=======
    global config_location
>>>>>>> 63632f9753caa8cd2aa6bc555b31e5748d31b87f
    print("Starting up... initializing machines for NUC with ID:", nucId)
    print("Base directory:", BASE_DIR)
    print("Fetching configuration from API server at:", NEBESTSERVERURL)
    try:
        config_url = f"https://{NEBESTSERVERURL}/api/Nuc/config/{nucId}"
        api_config = get_config_from_api(config_url)
        machines = load_machines(api_config["machines"])
        save_config_to_local(api_config)
        config_location = "API"
    except Exception as e:
        print(f"[FATAL] Could not fetch configuration from API: {e}")
        local_config = get_config_from_local()
        machines = load_machines(local_config["machines"])
        config_location = "LOCAL"

    buildmachines(machines)
    
    # hand over control to FastAPI
    yield
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

@app.get("/status")
def get_status():    
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
        "ip_address": get_local_ip(),
        "config_location": config_location,
        "machines": [
            {
                "device_id": machine.device_id,
                "name": machine.name,
                "comAddress": machine.comAddress,
                "connected": machine.get_status()
            }
            for machine in machinesAdapters
        ]
    }

@app.get("/logs")
def get_logs():
    log_path = BASE_DIR / "logs/stdout.log"

    if not os.path.exists(log_path):
        return Response(content=json.dumps({"error": f"Nuc API error: Log file not found"}), status_code=404, media_type="application/json")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return Response(content=json.dumps({"error": f"Nuc API error: {str(e)}"}), status_code=500, media_type="application/json")


@app.get("/read/{device}")
async def read(device: int):
    print(machinesAdapters)
    machine = next((machine for machine in machinesAdapters if machine.device_id == device), None)
    if machine is None:
        return Response(content=json.dumps({"error": f"Device {device} not found"}), status_code=404, media_type="application/json")

    print(f"Executing for {machine.device_id}")

    try:
        value = machine.get_data()
    except Exception as e:
        return Response(content=json.dumps({"error": f"Nuc API error: {str(e)}"}), status_code=409, media_type="application/json")
    print("Data:", value)

    return Response(content=json.dumps({
        "name":machine.name,
        "value": value
    }), status_code=200
    , media_type="application/json")

@app.websocket("/ws/{device}")
async def websocket_device(websocket: WebSocket, device: int):
    origin = websocket.headers.get("origin")
    print(f"Incoming WebSocket from {origin}")
    await websocket.accept()

    # Find the requested machine
    machine = next((m for m in machinesAdapters if m.device_id == device), None)
    if machine is None:
        await websocket.send_json({"error": f"Device {device} not found"})
        await websocket.close(code=1008)
        return

    # Check type
    if not isinstance(machine, SerialPortHandler):
        await websocket.send_json({"error": f"Device {device} is not a serial device"})
        await websocket.close(code=1008)
        return

    ser = machine.serialConnection
    if ser is None or not ser.is_open:
        await websocket.send_json({"event": "error", "message": "Serial port not open"})
        await websocket.close(code=1011)
        return

    # Claim exclusive ownership
    if hasattr(machine, "begin_stream") and not machine.begin_stream():
        await websocket.send_json({"event": "error", "message": "Device busy: already streaming"})
        await websocket.close(code=1013)
        return

    # Clear input buffer
    ser.reset_input_buffer()

    stop_event = asyncio.Event()

    # Background listener for client messages
    async def listen_client():
        try:
            while True:
                msg = await websocket.receive_text()
                print(f"Received message from client: {msg}")
                if msg.strip().lower() == "close":
                    print("Client requested stream stop.")
                    stop_event.set()
                    break
        except WebSocketDisconnect:
            stop_event.set()

    listener_task = asyncio.create_task(listen_client())

    try:
        i = 3
        while i > 0 and not stop_event.is_set():
            # line = await run_in_threadpool(ser.readline)
            line = await run_in_threadpool(ser.read_until, b'\r')
            print(f"Serial read line: {line}*")
            if not line:
                await asyncio.sleep(0.05)
                continue
            print(f"Read line: {line}")
            text = line.decode("utf-8", errors="replace").rstrip("\r\n")
            # value = device.parser(text) if device.parser else text

            value = text[5:]  # gives "42.02"
            await websocket.send_text(value)
            i -= 1

    except WebSocketDisconnect:
        print("WebSocket disconnected.")

    finally:
        stop_event.set()
        listener_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await listener_task

        if hasattr(machine, "end_stream"):
            machine.end_stream()

        if websocket.client_state != WebSocketState.DISCONNECTED:
            with contextlib.suppress(Exception):
                await websocket.close()

    print(f"WebSocket for {device} closed.")
    return

@app.websocket("/ws")
async def websocket_all_devices(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    print(f"Incoming aggregated WebSocket from {origin}")
    await websocket.accept()

    serial_devices = [m for m in machinesAdapters if isinstance(m, SerialPortHandler)]
    if not serial_devices:
        await websocket.send_json({"error": "No serial devices configured"})
        await websocket.close(code=1011)
        return

    active_devices: list[SerialPortHandler] = []
    busy_devices: list[int] = []
    offline_devices: list[int] = []

    for device in serial_devices:
        ser = device.serialConnection
        if ser is None or not ser.is_open:
            offline_devices.append(device.device_id)
            continue
        if hasattr(device, "begin_stream") and not device.begin_stream():
            busy_devices.append(device.device_id)
            continue
        active_devices.append(device)

    if not active_devices:
        message = "No serial devices available"
        details = []
        if offline_devices:
            details.append(f"offline: {', '.join(map(str, offline_devices))}")
        if busy_devices:
            details.append(f"busy: {', '.join(map(str, busy_devices))}")
        if details:
            message += f" ({'; '.join(details)})"
        await websocket.send_json({"error": message})
        await websocket.close(code=1013 if busy_devices else 1011)
        return

    if offline_devices:
        await websocket.send_json({"event": "warning", "message": f"Offline: {', '.join(map(str, offline_devices))}"})
    if busy_devices:
        await websocket.send_json({"event": "warning", "message": f"Busy: {', '.join(map(str, busy_devices))}"})

    await websocket.send_json({"event": "stream_started", "devices": [device.device_id for device in active_devices]})

    for device in active_devices:
        device.serialConnection.reset_input_buffer() # type: ignore

    stop_event = asyncio.Event()
    send_lock = asyncio.Lock()

    async def listen_client():
        try:
            while True:
                msg = await websocket.receive_text()
                if msg.strip().lower() == "close":
                    print("Client requested aggregated stream stop.")
                    stop_event.set()
                    break
        except WebSocketDisconnect:
            stop_event.set()

    async def stream_device(device: SerialPortHandler):
        ser = device.serialConnection
        assert ser is not None
        try:
            while not stop_event.is_set():
                line = await run_in_threadpool(ser.read_until, b"\r")
                if not line:
                    await asyncio.sleep(0.05)
                    continue
                text = line.decode("utf-8", errors="replace").rstrip("\r\n")
                print(f"Read from {device.device_id}: {text}")
                value = device.parser(text) if device.parser else text
                # value = text[5:] if len(text) > 5 else text
                # value = text
                if value is None:
                    continue
                try:
                    async with send_lock:
                        await websocket.send_json({"device": device.name, "value": value})
                except WebSocketDisconnect:
                    stop_event.set()
                    break
        except Exception as exc:
            print(f"Error streaming {device.device_id}: {exc}")
            stop_event.set()

    listener_task = asyncio.create_task(listen_client())
    stream_tasks = [asyncio.create_task(stream_device(device)) for device in active_devices]

    try:
        await stop_event.wait()
    finally:
        stop_event.set()
        listener_task.cancel()
        for task in stream_tasks:
            task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.gather(listener_task, *stream_tasks, return_exceptions=True)

        for device in active_devices:
            if hasattr(device, "end_stream"):
                device.end_stream()

        if websocket.client_state != WebSocketState.DISCONNECTED:
            with contextlib.suppress(Exception):
                await websocket.close()

    print("Aggregated WebSocket closed.")
    
    return

# ---- Entry point ----
if __name__ == "__main__":
    uvicorn.run("NucApi:app", host="0.0.0.0", port=8000, reload=False, log_level="info",
        ssl_keyfile=str(BASE_DIR / "certs/key.pem"),
        ssl_certfile=str(BASE_DIR / "certs/cert.pem"),
    )
