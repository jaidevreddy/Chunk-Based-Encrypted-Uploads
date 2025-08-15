import socket
import os
from encryption_utils import encrypt_chunk, load_aes_key

SERVER_IP = "192.168.64.3"  # Ubuntu server
PORT = 9191
CHUNK_SIZE = 4096  # 4KB

def send_encrypted_file(filename):
    aes_key = load_aes_key()

    with open(filename, "rb") as f:
        file_data = f.read()

    total_chunks = (len(file_data) + CHUNK_SIZE - 1) // CHUNK_SIZE

    s = socket.socket()
    s.connect((SERVER_IP, PORT))
    print("Connected to chunk upload server.")

    # Send filename and chunk info
    s.sendall(f"{os.path.basename(filename)}|{total_chunks}".encode())
    ack = s.recv(2)

    # Send encrypted chunks
    for i in range(total_chunks):
        chunk = file_data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
        encrypted = encrypt_chunk(chunk, aes_key)
        s.sendall(len(encrypted).to_bytes(4, 'big') + encrypted)
        print(f"📦 Sent encrypted chunk {i+1}/{total_chunks}")

    s.close()
    print("Encrypted file sent successfully.")

# Example usage
send_encrypted_file("Project_CP3_NetSec_RVU.pdf")  # replace with your test file
