import json
import base64
import os
import secrets
from fastapi import FastAPI, HTTPException, Request
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from utils.key_provider import load_private_key, load_public_key, setup_keys
from utils.logger import log_metadata

app = FastAPI(title="FinGuard API Gateway",
              description="Public API Gateway for FinGuard servers with E2E encryption.")

# Configuration from .env
FINANCIAL_SERVER_URL = os.getenv(
    "FINANCIAL_SERVER_URL", "http://localhost:8001")
NLP_SERVER_URL = os.getenv("NLP_SERVER_URL", "http://localhost:8000")
ANALYTICS_SERVER_URL = os.getenv(
    "ANALYTICS_SERVER_URL", "http://localhost:8002")

# Initialize keys
setup_keys()
private_key = load_private_key("keys/gateway_private_key.pem")
public_key = load_public_key("keys/gateway_public_key.pem")


def decrypt_request(encrypted_data: str, encrypted_key: str, iv: str):
    try:
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
        padded_data = decryptor.update(
            encrypted_data_bytes) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return json.loads(data.decode('utf-8'))
    except Exception as e:
        raise ValueError(f"Decryption error: {str(e)}")


def encrypt_response(response_data: dict, client_public_key):
    try:
        aes_key = secrets.randbits(256).to_bytes(32, 'big')
        iv = os.urandom(16)

        json_data = json.dumps(response_data).encode('utf-8')
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv),
                        backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        encrypted_key = client_public_key.encrypt(
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
    except Exception as e:
        raise ValueError(f"Encryption error: {str(e)}")


@app.post("/api/user-data")
async def get_user_data(request: Request):
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        user_id = decrypted.get("user_id")
        if not user_id:
            raise ValueError("Invalid request: user_id required")

        analytics_url = ANALYTICS_SERVER_URL + "/analytics/user-data"
        analytics_response = requests.post(
            analytics_url, json={"user_id": user_id})
        analytics_response.raise_for_status()
        response_data = analytics_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/user-data",
            "user_id": user_id,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/user-data",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/user-data",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/simulate")
async def simulate_investment(request: Request):
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        user_id = decrypted.get("user_id")
        simulation_data = decrypted.get("simulation_data")
        if not user_id or not simulation_data:
            raise ValueError(
                "Invalid request: user_id and simulation_data required")

        analytics_url = ANALYTICS_SERVER_URL + "/analytics/simulate"
        analytics_response = requests.post(
            analytics_url, json={"user_id": user_id, "simulation_data": simulation_data})
        analytics_response.raise_for_status()
        response_data = analytics_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/simulate",
            "user_id": user_id,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/simulate",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/simulate",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/recommend")
async def get_recommendations(request: Request):
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        user_id = decrypted.get("user_id")
        if not user_id:
            raise ValueError("Invalid request: user_id required")

        analytics_url = ANALYTICS_SERVER_URL + "/analytics/recommend"
        analytics_response = requests.post(
            analytics_url, json={"user_id": user_id})
        analytics_response.raise_for_status()
        response_data = analytics_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/recommend",
            "user_id": user_id,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/recommend",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/recommend",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/stock-sentiments")
async def analyze_stock_sentiments(request: Request):
    print(request)
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        # Only extract user_id, ignore stocks and scenario
        user_id = decrypted.get("user_id")
        if not user_id:
            raise ValueError("Invalid request: user_id required")

        # Use the modified request function
        nlp_url = NLP_SERVER_URL + "/nlp/user-stock-sentiments"
        nlp_response = requests.post(
            nlp_url,
            json={"userId": user_id},  # Changed to match the required format
            headers={"Content-Type": "application/json"}
        )
        nlp_response.raise_for_status()
        response_data = nlp_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-sentiments",
            "user_id": user_id,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-sentiments",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-sentiments",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/enhance")
async def enhance_simulation(request: Request):
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        simulation_data = decrypted.get("simulation_data")
        user_id = decrypted.get("user_id")
        ai_prompt = decrypted.get("ai_prompt")
        if not simulation_data or not user_id or not ai_prompt:
            raise ValueError(
                "Invalid request: simulation_data, user_id, and ai_prompt required")

        nlp_url = NLP_SERVER_URL + "/nlp/enhance"
        nlp_response = requests.post(nlp_url, json={
                                     "simulation_data": simulation_data, "user_id": user_id, "ai_prompt": ai_prompt})
        nlp_response.raise_for_status()
        response_data = nlp_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/enhance",
            "user_id": user_id,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/enhance",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/enhance",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/query")
async def process_query(request: Request):
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        query = decrypted.get("query")
        user_id = decrypted.get("user_id")
        if not query or not user_id:
            raise ValueError("Invalid request: query and user_id required")

        nlp_url = NLP_SERVER_URL + "/nlp/query"
        nlp_response = requests.post(
            nlp_url, json={"query": query, "user_id": user_id})
        nlp_response.raise_for_status()
        response_data = nlp_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/query",
            "user_id": user_id,
            "query_length": len(query),
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/query",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/query",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/stock-latest/{ticker}")
async def get_stock_latest(ticker: str, request: Request):
    try:
        body = await request.json() or {}  # Body is optional
        decrypted = decrypt_request(
            body.get("encrypted_data", ""),
            body.get("encrypted_key", ""),
            body.get("iv", "")
        ) if body else {}

        financial_url = FINANCIAL_SERVER_URL + f"/api/stock/latest/{ticker}"
        financial_response = requests.get(
            financial_url, json=decrypted or None)
        financial_response.raise_for_status()
        response_data = financial_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": f"/api/stock-latest/{ticker}",
            "ticker": ticker,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": f"/api/stock-latest/{ticker}",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": f"/api/stock-latest/{ticker}",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/stock-data")
async def get_stock_data(request: Request):
    try:
        body = await request.json()
        decrypted = decrypt_request(
            body.get("encrypted_data"),
            body.get("encrypted_key"),
            body.get("iv")
        )
        ticker = decrypted.get("ticker")
        start_date = decrypted.get("start_date")
        end_date = decrypted.get("end_date")
        if not ticker or not start_date or not end_date:
            raise ValueError(
                "Invalid request: ticker, start_date, and end_date required")

        financial_url = FINANCIAL_SERVER_URL + "/api/stock/data"
        financial_response = requests.post(financial_url, json={
                                           "ticker": ticker, "start_date": start_date, "end_date": end_date})
        financial_response.raise_for_status()
        response_data = financial_response.json()

        client_public_key = load_public_key("keys/client_public_key.pem")
        encrypted_response = encrypt_response(response_data, client_public_key)

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-data",
            "ticker": ticker,
            "status": "success"
        })
        return encrypted_response
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-data",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-data",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/public-key")
async def get_public_key():
    with open("keys/gateway_public_key.pem", "r") as f:
        return {"public_key": f.read()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
