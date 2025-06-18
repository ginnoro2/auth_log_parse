from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import os
import base64

# Define key paths
KEYS_DIR = 'keys'
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, 'private_key.pem')
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, 'public_key.pem')

def generate_key_pair():
    """Generate a new RSA key pair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

def save_keys(private_key, public_key):
    """Save the key pair to files"""
    os.makedirs(KEYS_DIR, exist_ok=True)
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(private_key)
    with open(PUBLIC_KEY_PATH, 'wb') as f:
        f.write(public_key)

def load_keys():
    """Load the key pair from files"""
    try:
        with open(PRIVATE_KEY_PATH, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        with open(PUBLIC_KEY_PATH, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        return private_key, public_key
    except FileNotFoundError:
        # Generate new keys if they don't exist
        private_pem, public_pem = generate_key_pair()
        save_keys(private_pem, public_pem)
        return load_keys()

def encrypt_data(data: str) -> bytes:
    """Encrypt a string using RSA"""
    if not data:
        return None
    _, public_key = load_keys()
    encrypted = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted)

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt encrypted data using RSA"""
    if not encrypted_data:
        return None
    private_key, _ = load_keys()
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted_data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()

# Generate keys on module import if they don't exist
if not (os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH)):
    private_pem, public_pem = generate_key_pair()
    save_keys(private_pem, public_pem) 