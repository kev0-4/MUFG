import requests
import json
import base64
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

# Constants
API_GATEWAY_URL = "http://20.244.41.104:8080"
PUBLIC_KEY_URL = f"{API_GATEWAY_URL}/api/public-key"
STOCK_SENTIMENTS_URL = f"{API_GATEWAY_URL}/api/stock-sentiments"

# Path to private key (same folder as script)
CLIENT_PRIVATE_KEY_PATH = "client_private_key.pem"


def load_private_key(path):
    """Load private key from file."""
    try:
        with open(path, "rb") as f:
            key_data = f.read()
            return serialization.load_pem_private_key(key_data, password=None)
    except Exception as e:
        print(f"Error loading private key: {e}")
        raise


def load_public_key(pem_data):
    """Load public key from PEM string."""
    try:
        return serialization.load_pem_public_key(pem_data.encode("utf-8"))
    except Exception as e:
        print(f"Error loading public key: {e}")
        raise


def validate_base64(data, label):
    """Validate base64-encoded string."""
    try:
        base64.b64decode(data)
        print(f"Validating {label}: Valid base64")
    except Exception as e:
        print(f"Validating {label}: Invalid base64: {e}")
        raise


def encrypt_request(data: dict, public_key):
    """Encrypt request data using AES and RSA."""
    try:
        aes_key = os.urandom(32)
        iv = os.urandom(16)
        json_data = json.dumps(data).encode("utf-8")

        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv),
                        backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode("utf-8"),
            "encrypted_key": base64.b64encode(encrypted_key).decode("utf-8"),
            "iv": base64.b64encode(iv).decode("utf-8"),
        }
    except Exception as e:
        print(f"Encryption failed: {e}")
        raise


def decrypt_response(encrypted_data: str, encrypted_key: str, iv: str, private_key):
    """Decrypt response data using AES and RSA."""
    try:
        validate_base64(encrypted_data, "encrypted_data")
        validate_base64(encrypted_key, "encrypted_key")
        validate_base64(iv, "iv")

        encrypted_data_bytes = base64.b64decode(encrypted_data)
        encrypted_key_bytes = base64.b64decode(encrypted_key)
        iv_bytes = base64.b64decode(iv)

        aes_key = private_key.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(
            iv_bytes), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(
            encrypted_data_bytes) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"Decryption failed: {e}")
        raise


def test_stock_sentiments():
    """Test the /api/stock-sentiments endpoint."""
    print("Testing FinGuard Stock Sentiments Endpoint")

    if not os.path.exists(CLIENT_PRIVATE_KEY_PATH):
        print(
            f"Error: Missing {CLIENT_PRIVATE_KEY_PATH}. Copy client_private_key.pem here.")
        return

    # Load client private key
    try:
        client_private_key = load_private_key(CLIENT_PRIVATE_KEY_PATH)
        print(f"Loaded client private key: {CLIENT_PRIVATE_KEY_PATH}")
    except Exception:
        return

    # Fetch server public key
    try:
        print(f"Fetching server public key from: {PUBLIC_KEY_URL}")
        response = requests.get(PUBLIC_KEY_URL, timeout=5)
        response.raise_for_status()
        public_key_data = response.json()
        if "public_key" not in public_key_data:
            raise ValueError("Public key not found in response")
        server_public_key = load_public_key(public_key_data["public_key"])
        print(f"Server public key fetched successfully.")
    except Exception as e:
        print(f"Failed to fetch server public key: {e}")
        return

    # Request data
    request_data = {"user_id": "uid1"}
    print(f"Request data: {request_data}")

    # Encrypt request
    try:
        encrypted_request = encrypt_request(request_data, server_public_key)
        print(f"Encrypted request ready.")
    except Exception:
        return

    # Send request
    try:
        print(f"Sending POST request to: {STOCK_SENTIMENTS_URL}")
        response = requests.post(STOCK_SENTIMENTS_URL,
                                 json=encrypted_request, timeout=5)
        print(f"HTTP Status: {response.status_code} {response.reason}")
        response.raise_for_status()
        response_data = response.json()
        print(f"Raw response: {response_data}")
    except Exception as e:
        print(f"Request error: {e}")
        return

    if not all(key in response_data for key in ["encrypted_data", "encrypted_key", "iv"]):
        print("Error: Response missing required fields: encrypted_data, encrypted_key, iv")
        return

    # Decrypt response
    try:
        decrypted_response = decrypt_response(
            response_data["encrypted_data"],
            response_data["encrypted_key"],
            response_data["iv"],
            client_private_key,
        )
        print(f"Decrypted response: {decrypted_response}")
    except Exception:
        print(
            "Action: Verify client_private_key.pem matches server’s client_public_key.pem")


if __name__ == "__main__":
    try:
        test_stock_sentiments()
        print("Test completed.")
    except Exception as e:
        print(f"Unexpected error: {e}")
