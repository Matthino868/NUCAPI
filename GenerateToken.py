import os
import base64
from datetime import datetime
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def _encrypt_string(key_bytes: bytes, iv_bytes: bytes, plain_text: str) -> str:
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded_data = pad(plain_text.encode("utf-8"), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode("utf-8")


def build_encrypted_token() -> str:
    token_base = os.getenv("CONFIGAPP_TOKEN")
    original_key = os.getenv("CONFIGAPP_ORIGINALKEY")
    vector_init = os.getenv("CONFIGAPP_VECTOR")

    if not token_base or not original_key or not vector_init:
        raise ValueError("Missing CONFIGAPP_TOKEN, CONFIGAPP_ORIGINALKEY, or CONFIGAPP_VECTOR")

    time_part = datetime.now().strftime("%d-%m-%Y %H")
    token = token_base + time_part

    key = original_key.encode("utf-8")
    iv = vector_init.encode("utf-8")

    return _encrypt_string(key, iv, token)


# def get_config_from_api(config_url: str) -> dict:
#     """
#     Fetch NUC configuration from the API using encrypted token header.
#     """

#     encrypted_token = _build_encrypted_token()

#     headers = {
#         "Accept": "application/json",
#         "X-Custom-Token": encrypted_token
#     }

#     resp = requests.get(config_url, verify=False, headers=headers)
#     print("Config data:", resp.text)
#     resp.raise_for_status()
#     return resp.json()

