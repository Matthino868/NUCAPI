import unittest
from fastapi.testclient import TestClient
import NucApi


client = TestClient(NucApi.app)

class FakeMachine(NucApi.MachineAdapter):
    def __init__(self, device_id=1, name="Fake Machine", comAddress="COM1"):
        self.device_id = device_id
        self.name = name
        self.comAddress = comAddress

    def get_status(self):
        return "Connected"

    def get_data(self):
        return 101.3
    


class TestMachineAPI(unittest.TestCase):
    def setUp(self):
        NucApi.machinesAdapters.clear()

    def test_get_status(self):
        fake_machine = FakeMachine()
        NucApi.machinesAdapters.append(fake_machine)
        
        response = client.get("/status")
        data = response.json()
        print("response code", response.status_code)
        print("response", data)
        self.assertEqual(response.status_code, 200)
        # self.assertIn("profile", data)
        self.assertIn("machines", data)
        self.assertIsInstance(data["machines"], list)

    def test_read_valid_device(self):
        fake_machine = FakeMachine()
        NucApi.machinesAdapters.append(fake_machine)

        response = client.get(f"/read/{fake_machine.device_id}")
        print("response", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(101.3, fake_machine.get_data())

    def test_read_invalid_device(self):
        response = client.get("/read/21")
        print("response", response.json())
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

if __name__ == "__main__":
    unittest.main()
