import requests
from MachineInterface import MachineInterface

class Compression(MachineInterface):
    def __init__(self, api_url, api_key, device_id, execCommand, name, comAddress):
        super().__init__(device_id=device_id, execCommand=execCommand, name=name, comAddress=comAddress)
        self.api_url = api_url
        self.api_key = api_key

    def get_test_acquired_data_and_results(self, test_number)->dict:
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "api_key": "CHANGE-ME-SOON",
                "device_id": self.device_id,
                "test_number": test_number
            },
            "method": "getTestAcquiredDataAndResults",
            "id": "1"
        }
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_data(self) -> int:
        # Check if test finished
        list_of_test = self.get_test_list()
        print("List of tests:", list_of_test)
        status = self.get_test_status(list_of_test[-1])
        print("Test finished:", status)
        if not status:
            raise Exception("Test not finished yet")
        # Get acquired data
        response_data = self.get_test_acquired_data_and_results(list_of_test[-1])
        max_value = max(point["value"] for point in response_data["result"]["list_of_channel_acquired_data"][0]["list_of_data_points"])
        return max_value+0.0001

    def get_test_status(self, test_number: int) -> bool:
        print("Fetching test status...")
        payload = {
            "jsonrpc": "2.0",
            "method": "getTestInfoAndStatus",
            "id": "1",
            "params": {
                "api_key": self.api_key,
                "device_id": self.device_id,
                "test_number": test_number
            },
        }
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        print("Response:", response.json())
        if response.json()["result"]["test_status_code"] != "END":
            return False
        return True
    
    def get_test_list(self) -> list[int]:
        print("Fetching test list...")
        payload = {
            "jsonrpc": "2.0",
            "method": "getListOfAllTests",
            "id": "1",
            "params": {
                "api_key": self.api_key,
                "device_id": self.device_id,

            },
        }
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        print("Response:", response.json())
        return response.json()["result"]["list_of_all_test_numbers"]

    def get_status(self) -> str:
        payload = {
            "jsonrpc": "2.0",
            "method": "getMachineStatus",
            "id": "1",
            "params": {
                "api_key": self.api_key,
                "device_id": self.device_id,
            },
        }
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return f"Statuscode {response.json()['result']['machine_status_id']}"
        except requests.RequestException as e:
            print(f"Error fetching machine status: {e}")
            return "Not connected"

    # def start_measurement(self) -> bool:
    #     payload = {
    #         "jsonrpc": "2.0",
    #         "method": "cloneAndStartNewTest",
    #         "id": "1",
    #         "params": {
    #             "api_key": self.api_key,
    #             "device_id": " CompressionBench01",
    #             "test_number": 5,
    #             "new_device_id": self.device_id,
    #             "test_description": "Betonblokken drukken",
    #             "specimen_code": None,
    #             "specimen_description": None,
    #             "sample_reception_epoch_time": int(time.time()),
    #             "customer_id": None
    #         },
    #     }
    #     response = requests.post(self.api_url, json=payload)
    #     response.raise_for_status()
    #     if response.json()["result"]["new_test_number"] is None:
    #         return False
    #     return True