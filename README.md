# Chunk-Based Encrypted Uploads

A secure, chunked file-upload system with hybrid cryptography (RSA for key exchange, AES for data), a macOS GUI client (Tkinter), Ubuntu servers (C), and MongoDB Atlas for user authentication and file metadata. Designed for large files and reliable transmission with integrity.

---

## Features
- **Hybrid cryptography:** RSA key exchange, per-session AES key for data encryption.
- **Chunked uploads:** Splits large files, encrypts each chunk, transmits, and reassembles on the server.
- **User authentication:** MongoDB Atlas stores hashed credentials and file metadata.
- **Cross-platform GUI:** Built with Tkinter for login, signup, and file uploads.
- **Dual secure channels:** 
  - Port `9100` → Key Exchange Server  
  - Port `9191` → Chunk Receiver Server  

---

## Architecture

1. Client generates RSA keypair → sends **public key** to Key Exchange Server.  
2. Server encrypts an **AES session key** with client public key → client decrypts with **private key**.  
3. Client splits file → **AES-encrypts** each chunk → sends to Chunk Receiver Server.  
4. Server **decrypts & reassembles** chunks → writes final file.  
5. MongoDB Atlas logs user + file metadata (username, file name, size, chunk count, timestamps).


---

## Required Dependencies

### Client (Python 3.10+)
- Python 3.10 or newer
- **Pip packages:** `pycryptodome`, `pymongo`, `python-dotenv`
- **Tkinter** (for GUI)
  - macOS (python.org installer includes Tk)
  - Ubuntu/Debian: `sudo apt-get install -y python3-tk`

### Servers (Ubuntu/Linux)
- Build tools: `gcc`, `make`, `pkg-config`
- OpenSSL headers: `libssl-dev`

### Install (Ubuntu/Debian):

- sudo apt-get update
- sudo apt-get install -y build-essential pkg-config libssl-dev
- git clone (https://github.com/jaidevreddy/Chunk-Based-Encrypted-Uploads)
- cd Chunk-Based-Encrypted-Uploads


### 2) Note the configuration values you’ll use

Replace the placeholders below with your actual values before running:

- `<MONGODB_URI>` — your MongoDB Atlas SRV connection string  
- `<KEY_EXCHANGE_HOST>` — host/IP of the Key Exchange Server (default port `9100`)  
- `<CHUNK_RECEIVER_HOST>` — host/IP of the Chunk Receiver Server (default port `9191`)  
- `<CHUNK_SIZE_BYTES>` — size of each chunk in bytes (e.g., `1048576` for 1 MiB)  

These values are read by the client code (via environment variables or arguments) depending on your implementation.  
If your client expects environment variables, export them as shown in **Step 4**.

### 3) Set up the client environment and libraries
- cd client
- python3 -m venv .venv
- source .venv/bin/activate
- pip install pycryptodome pymongo python-dotenv

# If Tkinter missing on Linux:
# sudo apt-get install -y python3-tk

### 5) Build the servers

- cd ../servers/key_exchange

- cd ../chunk_receiver

### 6) Create RSA key pairs (.pem)
Before running the servers, generate RSA key pairs for secure key exchange. Run this on the server (or client if your implementation requires local keys):

- openssl genrsa -out private_key.pem 2048  
- openssl rsa -in private_key.pem -pubout -out public_key.pem  

- Keep `private_key.pem` secret and never commit it to Git. Share `public_key.pem` where needed for encryption.

### 7) Run the servers
# Terminal A (key exchange)  
- cd servers/key_exchange  
  - ./key_exchange 9100  

# Terminal B (chunk receiver)  
- cd servers/chunk_receiver  
  - ./chunk_receiver 9191  

### 8) Launch the client GUI
- cd client  
- source .venv/bin/activate  
- python gui.py  

### 9) Use the app
- Login/Signup in the GUI.  
- Select a file → client performs RSA key exchange, encrypts chunks with AES, and uploads.  
- Verify the file and metadata in MongoDB Atlas (users + files collections).  

### Troubleshooting (quick)
- Handshake fails: verify server IP/ports and RSA keypair generation.  
- Corrupt output: confirm AES mode/IV/tag are identical on client and server.  
- Mongo errors: validate `MONGODB_URI` and IP allowlist in MongoDB Atlas.  
- Tkinter missing: install `python3-tk` on Linux.  



