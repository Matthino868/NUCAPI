import unittest
from unittest.mock import patch, MagicMock
import os
from NebestApi import get_config_from_api

class TestNebestServerAPI(unittest.TestCase):
    def setUp(self):
        self.test_nucid = "1"
        self.test_server_url = "10.80.131.67:20100"
        self.config_url = f"https://{self.test_server_url}/api/Nuc/config/{self.test_nucid}"
        self.mock_config_response = {
            "name": "nuc1",
            "machines": [
                {
                    "machineId": 1,
                    "name": "Weegschaal",
                    "comType": 3,
                    "comAddress": "5",
                    "nucId": 1
                }
            ]
        }

    @patch('NebestApi.requests.get')
    def test_get_config_from_api_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_config_response
        mock_get.return_value = mock_response

        result = get_config_from_api(self.config_url)

        mock_get.assert_called_once_with(self.config_url, verify=False)
        self.assertEqual(result, self.mock_config_response)
        self.assertIn("machines", result)

    @patch('NebestApi.requests.get')
    def test_get_config_from_api_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")

        with self.assertRaises(Exception):
            get_config_from_api(self.config_url)

    @patch('NebestApi.requests.get')
    def test_get_config_from_api_invalid_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            get_config_from_api(self.config_url)

    @patch.dict(os.environ, {"NEBESTSERVERURL": "10.80.131.67:20100", "NUCID": "1"})
    @patch('NebestApi.requests.get')
    def test_get_config_from_api_with_env_vars(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_config_response
        mock_get.return_value = mock_response

        nucid = os.getenv("NUCID", "0")
        server_url = os.getenv("NEBESTSERVERURL")
        config_url = f"https://{server_url}/api/Nuc/config/{nucid}"

        result = get_config_from_api(config_url)

        self.assertEqual(result, self.mock_config_response)

if __name__ == "__main__":
    unittest.main()
