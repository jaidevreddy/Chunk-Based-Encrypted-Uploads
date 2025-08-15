# socket_client.py
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

SERVER_IP = "192.168.64.3" 
PORT = 9100
KEY_DIR = "keys"
AES_KEY_FILE = "aes_key.bin"

def generate_rsa_keys():
    os.makedirs(KEY_DIR, exist_ok=True)
    private_key_file = os.path.join(KEY_DIR, "private.pem")
    public_key_file = os.path.join(KEY_DIR, "public.pem")

    if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
        key = RSA.generate(2048)
        with open(private_key_file, 'wb') as priv_file:
            priv_file.write(key.export_key())
        with open(public_key_file, 'wb') as pub_file:
            pub_file.write(key.publickey().export_key())
        print("🔐 RSA key pair generated.")
    else:
        print("✔️ RSA key pair already exists.")

def send_public_key_and_receive_encrypted_aes():
    try:
        public_key_path = os.path.join(KEY_DIR, "public.pem")
        private_key_path = os.path.join(KEY_DIR, "private.pem")

        print(f"🛰️ Trying to connect to {SERVER_IP}:{PORT} ...")
        s = socket.socket()
        s.connect((SERVER_IP, PORT))
        print("🌐 Connected to server.")

        with open(public_key_path, 'rb') as f:
            pubkey_data = f.read()
            s.sendall(pubkey_data)
            print("📤 Public key sent to server.")

        encrypted_aes = s.recv(512)
        print("📥 Received encrypted AES key.")

        with open(private_key_path, 'rb') as f:
            priv_key = RSA.import_key(f.read())
            cipher_rsa = PKCS1_OAEP.new(priv_key)
            aes_key = cipher_rsa.decrypt(encrypted_aes)

        with open(AES_KEY_FILE, 'wb') as f:
            f.write(aes_key)

        print(f"✅ AES Session Key (decrypted): {aes_key.hex()}")
        return aes_key

    except Exception as e:
        print(f"❌ Error during key exchange: {e}")
        return None

# 👇 ONLY generate keys, don't connect or send anything yet
generate_rsa_keys()