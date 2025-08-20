import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

KEY_DIR = "keys"
GATEWAY_PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "gateway_private_key.pem")
GATEWAY_PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "gateway_public_key.pem")
CLIENT_PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "client_private_key.pem")
CLIENT_PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "client_public_key.pem")

def generate_and_save_keypair(private_path: str, public_path: str):
    """Generate RSA keypair and save to files."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Save private key
    with open(private_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save public key
    with open(public_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def setup_keys():
    """Create key directory and generate keypairs if they don't exist."""
    if not os.path.exists(KEY_DIR):
        os.makedirs(KEY_DIR)
    
    if not os.path.exists(GATEWAY_PRIVATE_KEY_PATH) or not os.path.exists(GATEWAY_PUBLIC_KEY_PATH):
        generate_and_save_keypair(GATEWAY_PRIVATE_KEY_PATH, GATEWAY_PUBLIC_KEY_PATH)
    
    if not os.path.exists(CLIENT_PRIVATE_KEY_PATH) or not os.path.exists(CLIENT_PUBLIC_KEY_PATH):
        generate_and_save_keypair(CLIENT_PRIVATE_KEY_PATH, CLIENT_PUBLIC_KEY_PATH)

def load_private_key(path: str):
    """Load RSA private key from file."""
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

def load_public_key(path: str):
    """Load RSA public key from file."""
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )

if __name__ == "__main__":
    setup_keys()
    print(f"Keys generated and saved in {KEY_DIR}/")