import os
import socket
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

SERVER_IP = "192.168.64.3"  # Replace with your Ubuntu IP
PORT = 9191
CHUNK_SIZE = 4096  # 4KB per chunk

def pad(data):
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def encrypt_chunk(chunk, aes_key):
    iv = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(chunk))
    return iv + encrypted  # prepend IV

def send_chunks(file_path, aes_key):
    s = socket.socket()
    s.connect((SERVER_IP, PORT))

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

    print(f"🌐 Connected to server for chunk upload.")
    s.sendall(f"{filename}|{total_chunks}".encode())
    ack = s.recv(2)

    if ack != b"OK":
        print("Server did not acknowledge.")
        s.close()
        return 0

    chunks_sent = 0
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            encrypted = encrypt_chunk(chunk, aes_key)
            chunk_len = len(encrypted).to_bytes(4, 'big')
            s.sendall(chunk_len + encrypted)
            chunks_sent += 1
            print(f"Chunk {chunks_sent}/{total_chunks} sent")

    s.close()
    print("📦 File upload complete.")
    return chunks_sent

def encrypt_and_upload_chunks(file_path, aes_key):
    return send_chunks(file_path, aes_key)
