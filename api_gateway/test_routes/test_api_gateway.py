import requests
import json
import base64
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# Constants
API_GATEWAY_URL = "http://20.244.41.104:8080"
PUBLIC_KEY_URL = f"{API_GATEWAY_URL}/api/public-key"
CLIENT_PRIVATE_KEY_PATH = "client_private_key.pem"

# Endpoints
ENDPOINTS = {
    "user-data": f"{API_GATEWAY_URL}/api/user-data",
    "simulate": f"{API_GATEWAY_URL}/api/simulate",
    "recommend": f"{API_GATEWAY_URL}/api/recommend",
    "stock-sentiments": f"{API_GATEWAY_URL}/api/stock-sentiments",
    "enhance": f"{API_GATEWAY_URL}/api/enhance",
    "query": f"{API_GATEWAY_URL}/api/query",
    "stock-latest": f"{API_GATEWAY_URL}/api/stock-latest/AAPL",
    "stock-data": f"{API_GATEWAY_URL}/api/stock-data",
    "public-key": f"{API_GATEWAY_URL}/api/public-key",
    "test": f"{API_GATEWAY_URL}/api/test"
}


def load_private_key(path):
    try:
        with open(path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to load private key: {e}")
        raise


def load_public_key(pem_data):
    try:
        return serialization.load_pem_public_key(pem_data.encode("utf-8"))
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to load public key: {e}")
        raise


def validate_base64(data, label):
    try:
        base64.b64decode(data)
        print(Fore.GREEN + f"[OK] {label} is valid base64")
    except Exception as e:
        print(Fore.RED + f"[ERROR] {label} invalid base64: {e}")
        raise


def encrypt_request(data: dict, public_key):
    try:
        aes_key = os.urandom(32)
        iv = os.urandom(16)
        json_data = json.dumps(data).encode("utf-8")

        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
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

        print(Fore.CYAN + "[INFO] Request encrypted successfully")
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode("utf-8"),
            "encrypted_key": base64.b64encode(encrypted_key).decode("utf-8"),
            "iv": base64.b64encode(iv).decode("utf-8"),
        }
    except Exception as e:
        print(Fore.RED + f"[ERROR] Encryption failed: {e}")
        raise


def decrypt_response(encrypted_data: str, encrypted_key: str, iv: str, private_key):
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

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv_bytes), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data_bytes) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        print(Fore.CYAN + "[INFO] Response decrypted successfully")
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print(Fore.RED + f"[ERROR] Decryption failed: {e}")
        raise


def test_endpoint(endpoint_name, method, url, request_data=None):
    print(Fore.MAGENTA + f"\n=== Testing {endpoint_name.upper()} ({method} {url}) ===")

    # Load client private key
    client_private_key = None
    if endpoint_name not in ["public-key", "test"]:
        if not os.path.exists(CLIENT_PRIVATE_KEY_PATH):
            print(Fore.RED + f"[ERROR] Missing {CLIENT_PRIVATE_KEY_PATH}")
            return False
        client_private_key = load_private_key(CLIENT_PRIVATE_KEY_PATH)
        print(Fore.GREEN + f"[OK] Loaded client private key")

    # Fetch server public key
    server_public_key = None
    if endpoint_name not in ["public-key", "test"]:
        try:
            response = requests.get(PUBLIC_KEY_URL, timeout=5510)
            response.raise_for_status()
            public_key_data = response.json()
            if "public_key" not in public_key_data:
                raise ValueError("Missing 'public_key' in response")
            server_public_key = load_public_key(public_key_data["public_key"])
            print(Fore.GREEN + "[OK] Server public key fetched")
        except Exception as e:
            print(Fore.RED + f"[ERROR] Failed to fetch public key: {e}")
            return False

    # Encrypt request if needed
    encrypted_request = None
    if request_data:
        print(Fore.BLUE + f"[REQUEST] {request_data}")
        try:
            encrypted_request = encrypt_request(request_data, server_public_key)
        except Exception:
            return False

    # Send request
    try:
        if method == "POST":
            response = requests.post(url, json=encrypted_request, timeout=5520)
        else:
            response = requests.get(url, timeout=5520)
        print(Fore.YELLOW + f"[HTTP] {response.status_code} {response.reason}")
        response.raise_for_status()
        response_data = response.json()
        print(Fore.BLUE + f"[RAW RESPONSE] {response_data}")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Request failed: {e}")
        return False

    # Process response
    if endpoint_name in ["public-key", "test"]:
        print(Fore.CYAN + f"[INFO] Response: {response_data}")
    else:
        if not all(k in response_data for k in ["encrypted_data", "encrypted_key", "iv"]):
            print(Fore.RED + "[ERROR] Response missing required fields")
            return False
        try:
            decrypted_response = decrypt_response(
                response_data["encrypted_data"],
                response_data["encrypted_key"],
                response_data["iv"],
                client_private_key,
            )
            print(Fore.GREEN + f"[DECRYPTED] {decrypted_response}")
        except Exception:
            print(Fore.RED + "[ERROR] Decryption failed – check client_private_key.pem")
            return False

    return True


def test_all_endpoints():
    print(Style.BRIGHT + Fore.MAGENTA + "\n=== Testing All FinGuard API Endpoints ===")

    test_cases = [
        {"name": "public-key", "method": "GET", "url": ENDPOINTS["public-key"], "data": None},
        {"name": "user-data", "method": "POST", "url": ENDPOINTS["user-data"], "data": {"user_id": "uid1"}},
        {"name": "simulate", "method": "POST", "url": ENDPOINTS["simulate"], "data": {"user_id": "uid1", "simulation_data": {"amount": 10000, "stocks": ["AAPL", "GOOGL"], "duration_months": 12}}},
        {"name": "recommend", "method": "POST", "url": ENDPOINTS["recommend"], "data": {"user_id": "uid1"}},
        {"name": "stock-sentiments", "method": "POST", "url": ENDPOINTS["stock-sentiments"], "data": {"user_id": "uid1"}},
        {"name": "enhance", "method": "POST", "url": ENDPOINTS["enhance"], "data": {"user_id": "uid1", "simulation_data": {"amount": 10000, "stocks": ["AAPL"]}, "ai_prompt": "Optimize for low risk"}},
        {"name": "query", "method": "POST", "url": ENDPOINTS["query"], "data": {"user_id": "uid1", "query": "What is the stock market outlook for tech?"}},
        {"name": "stock-latest", "method": "GET", "url": ENDPOINTS["stock-latest"], "data": {"user_id": "uid1"}},
        {"name": "stock-data", "method": "POST", "url": ENDPOINTS["stock-data"], "data": {"ticker": "AAPL", "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), "end_date": datetime.now().strftime("%Y-%m-%d")}},
        {"name": "test", "method": "GET", "url": ENDPOINTS["test"], "data": None},
    ]

    results = []
    for case in test_cases:
        success = test_endpoint(case["name"], case["method"], case["url"], case["data"])
        results.append({"endpoint": case["name"], "success": success})
        print(Fore.GREEN + f"[SUCCESS] {case['name']}" if success else Fore.RED + f"[FAILED] {case['name']}")

    success_count = sum(r["success"] for r in results)
    print(Style.BRIGHT + Fore.MAGENTA + f"\n=== Test Summary: {success_count}/{len(results)} succeeded ===")
    for r in results:
        status = Fore.GREEN + "Success" if r["success"] else Fore.RED + "Failed"
        print(f"{r['endpoint']}: {status}")


if __name__ == "__main__":
    try:
        test_all_endpoints()
        print(Style.BRIGHT + Fore.CYAN + "\nAll tests completed.")
    except Exception as e:
        print(Fore.RED + f"[FATAL] Unexpected error: {e}")
