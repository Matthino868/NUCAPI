from enum import Enum
import requests
import json
from Models import Machine, MachineAdapterType  



def save_config_to_local(machines: dict[int, Machine], filename="nuc_config.json"):
    """
    Save the current machine configuration to a local JSON file.
    """
    try:
        # data = {}
        # for k, v in machines.items():
        #     d = v.dict()
        #     if isinstance(d["comType"], Enum):
        #         d["comType"] = d["comType"].value   # or .name if you prefer
        #     data[k] = d

        with open(filename, 'w') as f:
            json.dump(machines, f, indent=4)

        print(f"Configuration saved to {filename}")
    except Exception as e:
        print(f"Error saving configuration to file: {e}")

def load_machines(config_machines: list[dict]) -> dict[int, Machine]:
    """
    Load machines from configuration data and return as a dictionary.
    """
    machines = dict[int, Machine]()
    try:
        for m in config_machines:
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

def get_config_from_api(config_url: str )-> dict:
    """
    Fetch NUC configuration from the API and return as a dictionary.
    """        

    resp = requests.get(config_url, verify=False)
    resp.raise_for_status()
    data = resp.json()
    print("Config data:", data)
    return data

def get_config_from_local(filename="nuc_config.json")-> dict:
    """
    Load NUC configuration from a local JSON file and return as a dictionary.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading config from local file: {e}")
        return {}