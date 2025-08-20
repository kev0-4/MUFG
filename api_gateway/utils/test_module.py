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
    """Test a single endpoint and return results"""
    setup_keys()
    client_private_key = load_private_key("keys/client_private_key.pem")

    result = {
        "endpoint": endpoint,
        "method": method,
        "status": "success",
        "request_data": request_data,
        "response": None,
        "error": None,
        "status_code": None
    }

    try:
        # Get public key from gateway
        response = requests.get(PUBLIC_KEY_URL)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w") as temp_file:
            temp_file.write(response.json()["public_key"])
            temp_file_path = temp_file.name

        try:
            gateway_public_key = load_public_key(temp_file_path)
            encrypted_request = encrypt_request(request_data, gateway_public_key)

            # Send request
            if method == "POST":
                response = requests.post(
                    f"{API_GATEWAY_BASE_URL}{endpoint}", json=encrypted_request)
            else:
                response = requests.get(
                    f"{API_GATEWAY_BASE_URL}{endpoint}", json=encrypted_request)
            
            result["status_code"] = response.status_code
            response.raise_for_status()
            response_data = response.json()

            decrypted_response = decrypt_response(
                response_data["encrypted_data"],
                response_data["encrypted_key"],
                response_data["iv"],
                client_private_key
            )
            
            result["response"] = decrypted_response
            
        except requests.exceptions.RequestException as re:
            result["status"] = "error"
            result["error"] = str(re)
        except ValueError as ve:
            result["status"] = "error"
            result["error"] = str(ve)
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Failed to get public key: {str(e)}"

    return result


def run_all_tests():
    """Run all test endpoints and return results"""
    test_results = []
    
    # Test all endpoints
    endpoints = [
        ("/api/stock-sentiments", {"user_id": "uid1"}, "POST"),
        ("/api/user-data", {"user_id": "uid1"}, "POST"),
        ("/api/simulate", {"user_id": "uid1", "simulation_data": {
            "projected_balance": 360000.45, "timeframe": 10}}, "POST"),
        ("/api/recommend", {"user_id": "uid1"}, "POST"),
        ("/api/enhance", {"simulation_data": {"projected_balance": 360000.45,
            "timeframe": 10}, "user_id": "uid1", "ai_prompt": "Use a savings analogy."}, "POST"),
        ("/api/query", {"query": "BHP.AX recession", "user_id": "uid1"}, "POST"),
        ("/api/stock-latest/INTC", {"ticker": "INTC", "start_date": "2024-06-19", "end_date": "2025-08-19"}, "GET"),
        ("/api/stock-data", {"ticker": "INTC", "start_date": "2025-07-20", "end_date": "2025-08-15"}, "POST")
    ]
    
    for endpoint, data, method in endpoints:
        print(f"-------------running test for {endpoint} --------------")
        result = test_endpoint(endpoint, data, method)
        test_results.append(result)
        print(f"------------- Test for {endpoint} finished --------------")

    
    return test_results