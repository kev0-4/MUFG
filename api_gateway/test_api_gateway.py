import requests
import json
import base64
import os
import tempfile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from utils.key_provider import load_private_key, load_public_key, setup_keys

API_GATEWAY_BASE_URL = "http://localhost:8080"
PUBLIC_KEY_URL = f"{API_GATEWAY_BASE_URL}/api/public-key"

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def short_print(label, obj, limit=150, color=Colors.WHITE):
    """Print object truncated to `limit` characters with color."""
    text = str(obj)
    if len(text) > limit:
        text = text[:limit] + "..."
    print(f"{color}{label} {text}{Colors.RESET}")


def encrypt_request(data: dict, public_key):
    aes_key = os.urandom(32)
    iv = os.urandom(16)

    json_data = json.dumps(data).encode('utf-8')
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
            label=None
        )
    )

    return {
        "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8'),
        "encrypted_key": base64.b64encode(encrypted_key).decode('utf-8'),
        "iv": base64.b64encode(iv).decode('utf-8')
    }


def decrypt_response(encrypted_data: str, encrypted_key: str, iv: str, private_key):
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    encrypted_key_bytes = base64.b64decode(encrypted_key)
    iv_bytes = base64.b64decode(iv)

    aes_key = private_key.decrypt(
        encrypted_key_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(
        iv_bytes), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return json.loads(data.decode('utf-8'))


def test_endpoint(endpoint: str, request_data: dict, method: str = "POST"):
    setup_keys()
    client_private_key = load_private_key("keys/client_private_key.pem")

    # Get public key from gateway
    print(f"{Colors.CYAN}{Colors.BOLD}\n{'='*80}")
    print(f"Testing endpoint: {endpoint}")
    print(f"Method: {method}")
    print(f"{'='*80}{Colors.RESET}")
    
    response = requests.get(PUBLIC_KEY_URL)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w") as temp_file:
        temp_file.write(response.json()["public_key"])
        temp_file_path = temp_file.name

    try:
        gateway_public_key = load_public_key(temp_file_path)
        encrypted_request = encrypt_request(request_data, gateway_public_key)
        short_print(f"Encrypted request:", encrypted_request, color=Colors.YELLOW)

        # Send request
        print(f"{Colors.BLUE}Sending {method} request to {endpoint}...{Colors.RESET}")
        if method == "POST":
            response = requests.post(
                f"{API_GATEWAY_BASE_URL}{endpoint}", json=encrypted_request)
        else:
            response = requests.get(
                f"{API_GATEWAY_BASE_URL}{endpoint}", json=encrypted_request)
        
        short_print(f"HTTP Status:", f"{response.status_code} {response.reason}", 
                   color=Colors.GREEN if response.status_code == 200 else Colors.RED)
        
        response.raise_for_status()
        response_data = response.json()

        decrypted_response = decrypt_response(
            response_data["encrypted_data"],
            response_data["encrypted_key"],
            response_data["iv"],
            client_private_key
        )
        short_print(f"Decrypted response:", decrypted_response, color=Colors.GREEN)
        
    except requests.exceptions.RequestException as re:
        short_print(f"Request error:", str(re), color=Colors.RED)
    except ValueError as ve:
        short_print(f"Decryption error:", str(ve), color=Colors.RED)
    except Exception as e:
        short_print(f"Error:", str(e), color=Colors.RED)
    finally:
        os.unlink(temp_file_path)
    
    # Wait for user input before proceeding
    print(f"{Colors.MAGENTA}{Colors.BOLD}\nPress Enter to continue to the next endpoint...{Colors.RESET}")
    input()


def test_api_gateway():
    # Test all endpoints
    test_endpoint("/api/stock-sentiments",
                  { "user_id": "uid1"})
    test_endpoint("/api/user-data", {"user_id": "uid1"})
    test_endpoint("/api/simulate", {"user_id": "uid1", "simulation_data": {
                  "projected_balance": 360000.45, "timeframe": 10}})
    test_endpoint("/api/recommend", {"user_id": "uid1"})
    
    test_endpoint("/api/enhance", {"simulation_data": {"projected_balance": 360000.45,
                  "timeframe": 10}, "user_id": "uid1", "ai_prompt": "Use a savings analogy."})
    test_endpoint(
        "/api/query", {"query": "BHP.AX recession", "user_id": "uid1"})
    test_endpoint("/api/stock-latest/INTC",
                  {"ticker": "INTC", "start_date": "2024-06-19", "end_date": "2025-08-19"}, method="GET")
    test_endpoint("/api/stock-data", {"ticker": "INTC",
                  "start_date": "2025-07-20", "end_date": "2025-08-15"})


if __name__ == "__main__":
    test_api_gateway()