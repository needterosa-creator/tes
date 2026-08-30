import hashlib, os, base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def grafana_derive_key(secret_key):
    """Derive AES key from Grafana secret_key using PBKDF2"""
    return hashlib.pbkdf2_hmac('sha256', secret_key.encode(), b'aes-256-cfb', 10000, dklen=32)

def grafana_decrypt(encrypted_b64, secret_key):
    """Decrypt Grafana encrypted value"""
    try:
        raw = base64.b64decode(encrypted_b64)
        key = grafana_derive_key(secret_key)
        iv = raw[:16]
        ciphertext = raw[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')
    except Exception as e:
        return f"FAIL: {e}"

def grafana_encrypt(plaintext, secret_key):
    """Encrypt value using Grafana method"""
    key = grafana_derive_key(secret_key)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode()

# Test with default Grafana secret_key
DEFAULT_KEY = "SW2YcwTIb9zpOOhoPsMm"
known_password = "Passwd2024!"

# Encrypt known password
encrypted = grafana_encrypt(known_password, DEFAULT_KEY)
print(f"Encrypted with default key: {encrypted}")

# Decrypt back
decrypted = grafana_decrypt(encrypted, DEFAULT_KEY)
print(f"Decrypted back: {decrypted}")
print(f"Match: {decrypted == known_password}")
