import tkinter as tk
from tkinter import filedialog, messagebox
import os
from db import signup, login, log_upload_metadata
from socket_client import send_public_key_and_receive_encrypted_aes
from chunk_uploader import encrypt_and_upload_chunks

logged_in_user = None
aes_key = None
file_path_var = None
status_label = None

app = tk.Tk()
app.title("Secure Chunk Uploader")
app.geometry("400x300")
app.resizable(False, False)
app.configure(bg="#f4f4f4")

def handle_signup():
    username = username_entry.get()
    password = password_entry.get()
    success, msg = signup(username, password)
    status_label.config(text=msg, fg="green" if success else "red")

def handle_login():
    global logged_in_user, aes_key
    username = username_entry.get()
    password = password_entry.get()
    success, msg = login(username, password)
    if success:
        logged_in_user = username
        aes_key = send_public_key_and_receive_encrypted_aes()
        if aes_key:
            show_upload_screen()
        else:
            messagebox.showerror("Error", "AES key not received. Try again later.")
    else:
        status_label.config(text=msg, fg="red")

def pick_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)

def upload_file():
    file_path = file_path_var.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    chunks_uploaded = encrypt_and_upload_chunks(file_path, aes_key)

    log_upload_metadata(logged_in_user, filename, chunks_uploaded, file_size)
    messagebox.showinfo("Success", f"{filename} uploaded successfully.")

def show_auth_screen():
    clear_screen()
    tk.Label(app, text="Username:", bg="#f4f4f4").pack(pady=(30, 5))
    global username_entry
    username_entry = tk.Entry(app)
    username_entry.pack()

    tk.Label(app, text="Password:", bg="#f4f4f4").pack(pady=5)
    global password_entry
    password_entry = tk.Entry(app, show="*")
    password_entry.pack()

    tk.Button(app, text="Login", command=handle_login, width=10).pack(pady=(15, 5))
    tk.Button(app, text="Signup", command=handle_signup, width=10).pack()

    global status_label
    status_label = tk.Label(app, text="", bg="#f4f4f4", fg="green")
    status_label.pack(pady=10)

def show_upload_screen():
    clear_screen()
    tk.Label(app, text=f"Welcome, {logged_in_user}", font=("Arial", 12, "bold"), bg="#f4f4f4").pack(pady=(30, 5))
    tk.Button(app, text="Select File", command=pick_file).pack(pady=10)

    global file_path_var
    file_path_var = tk.StringVar()
    tk.Entry(app, textvariable=file_path_var, width=40).pack()

    tk.Button(app, text="Upload", command=upload_file, bg="#4CAF50", fg="white", width=15).pack(pady=20)

def clear_screen():
    for widget in app.winfo_children():
        widget.destroy()

# Start GUI
show_auth_screen()
app.mainloop()