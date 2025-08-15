from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os

def load_aes_key(path="aes_key.bin"):
    with open(path, "rb") as f:
        return f.read()

def encrypt_chunk(chunk, key):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(chunk, AES.block_size))
    return iv + ciphertext  # prepend IV

def decrypt_chunk(data, key):
    iv = data[:16]
    ciphertext = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)