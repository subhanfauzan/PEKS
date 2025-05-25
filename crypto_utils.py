# crypto_utils.py

import hashlib
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Generate RSA Keys (simpan saat pertama kali)
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def save_keys(private_key, public_key):
    with open("private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_keys():
    with open("private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open("public.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return private_key, public_key

# PEKS index dari keyword
def generate_index(keyword, public_key):
    keyword_hash = hashlib.sha256(keyword.encode()).digest()
    encrypted_index = public_key.encrypt(
        keyword_hash,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return encrypted_index

# Trapdoor untuk pencarian
def generate_trapdoor(keyword):
    return hashlib.sha256(keyword.encode()).digest()

# Pencocokan trapdoor dengan index PEKS
def match(index, trapdoor, private_key):
    try:
        decrypted = private_key.decrypt(
            index,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        return decrypted == trapdoor
    except Exception:
        return False
