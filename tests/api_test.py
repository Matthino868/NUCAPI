import unittest
from fastapi.testclient import TestClient
import json

import machine_api  # This imports your FastAPI app

client = TestClient(machine_api.app)

class TestMachineAPI(unittest.TestCase):

    def test_get_devices(self):
        response = client.get("/devices")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_get_config(self):
        response = client.get("/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("name", data)
        self.assertIn("devices", data)

    

    def test_update_config_invalid(self):
        with open("tests/invalid_configs.json", "r") as f:
            invalid_configs = json.load(f)

        for invalid_config in invalid_configs:
            response = client.post("/config", json=invalid_config)
            print(response.json())
            self.assertEqual(response.status_code, 422)

    def test_update_config(self):
        new_config = {
            "name": "Compression NUC",
            "description": "Controls the compression process",
            "devices": {
                "scale01": {
                    "comAddress": "3",
                    "name": "Ohaus weegschaal",
                    "description": "Compression test scale",
                    "comType": "usb",
                    "execCommand": "s"
                },
                "caliper01": {
                    "comAddress": "7",
                    "name": "Caliper",
                    "description": "Caliper profile",
                    "comType": "usb",
                    "execCommand": "0"
                },
                "CompressionBench01": {
                    "id": "CompressionBench01",
                    "name": "Compression bench",
                    "execCommand": "MEASURE",
                    "description": "Compression test scale",
                    "comType": "ethernet",
                    "comAddress": "0.0.0.0"
                }
            }
        }
        response = client.post("/config", json=new_config)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Configuration updated", str(response.json()))

    def test_get_status(self):
        response = client.get("/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("profile", data)
        self.assertIn("machines", data)
        self.assertIsInstance(data["machines"], list)

    def test_read_invalid_device(self):
        response = client.get("/read/NonExistentDevice")
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.json())

if __name__ == "__main__":
    unittest.main()
