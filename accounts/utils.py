from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import os

def _get_key(key_str):
    # Hash key string to 32 bytes
    return hashlib.sha256(key_str.encode()).digest()

def encrypt_file(file_path, key_str):
    key = _get_key(key_str)
    with open(file_path, "rb") as f:
        data = f.read()
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    with open(file_path, "wb") as f:
        for x in (cipher.nonce, tag, ciphertext):
            f.write(x)

def decrypt_file(enc_path, dec_path, key_str):
    key = _get_key(key_str)
    with open(enc_path, "rb") as f:
        nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]
        if len(ciphertext) == 0:
            ciphertext = f.read()  # fallback
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    with open(dec_path, "wb") as f:
        f.write(data)
