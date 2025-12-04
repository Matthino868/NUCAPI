from enum import Enum
import requests
import json
from Models import Machine, MachineAdapterType  

def save_config_to_local(machines: dict[int, Machine], filename="nuc_config.json"):
    try:
        data = {}
        for k, v in machines.items():
            d = v.dict()
            if isinstance(d["comType"], Enum):
                d["comType"] = d["comType"].value   # or .name if you prefer
            data[k] = d

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Configuration saved to {filename}")
    except Exception as e:
        print(f"Error saving configuration to file: {e}")

def load_machines(config: list[dict]):
    machines = dict[int, Machine]()
    try:
        for m in config:
            key = m['machineId']  # machine01, machine02, etc.

            machines[key] = Machine(
                    # machineId=m["machineId"], 
                    name=m["name"], 
                    comType=MachineAdapterType(m["comType"]), 
                    comAddress=m["comAddress"], 
                    nucId=m["nucId"])
        print("Config machines:", machines)
        return machines
    except Exception as e:
        print("Error fetching config:", e)
        return dict[int, Machine]()

def get_config_from_api(config_url="https://10.80.131.168:20100/api/Nuc/config/0"):
    """
    Fetch NUC configuration from the API and return as a dictionary.
    """
    
    resp = requests.get(config_url, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return data["machines"]

def get_config_from_local(filename="nuc_config.json"):
    """
    Load NUC configuration from a local JSON file and return as a dictionary.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return [v for k, v in data.items()]
    except Exception as e:
        print(f"Error loading config from local file: {e}")
        return []