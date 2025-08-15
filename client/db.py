# Client/db.py
import hashlib
from pymongo import MongoClient
from datetime import datetime

# Replace with your own MongoDB URI
MONGO_URI = "mongodb+srv://Jaidev:V8VGPn0TMSGEd4vR@cluster0.zpmzs.mongodb.net/?retryWrites=true&w=majority&ssl=true&sslInvalidHostNameAllowed=true"
client = MongoClient(MONGO_URI)
db = client["ChunkUploader"]
users = db["users"]
uploads = db["uploads"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    if users.find_one({"username": username}):
        return False, "Username already exists."
    users.insert_one({
        "username": username,
        "password": hash_password(password),
        "role": "user",
        "created_at": datetime.utcnow()
    })
    return True, "Signup successful."

def login(username, password):
    user = users.find_one({"username": username})
    if user and user["password"] == hash_password(password):
        return True, "Login successful."
    return False, "Invalid credentials."

def log_upload_metadata(username, filename, chunk_count, file_size):
    uploads.insert_one({
        "filename": filename,
        "chunk_count": chunk_count,
        "file_size": file_size,
        "uploaded_by": username,
        "upload_date": datetime.utcnow()
    })