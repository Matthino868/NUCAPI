import unittest
from fastapi.testclient import TestClient

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

    def test_update_config(self):
        new_config = {
            "name": "TestNUC",
            "description": "Updated test config",
            "devices": {}
        }
        response = client.post("/config", json=new_config)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Configuration updated", str(response.json()))

    def test_update_config_invalid(self):
        invalid_config = {
            "name": "InvalidNUC",
            # Missing 'description' and 'devices'
        }
        response = client.post("/config", json=invalid_config)
        print(response.json())
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity for validation errors

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
