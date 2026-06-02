import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Ambil kunci AES dari .env
aes_key = os.getenv('AES_SECRET_KEY')

if not aes_key:
    raise ValueError("AES_SECRET_KEY tidak ditemukan di environment variables!")

# Inisialisasi Fernet cipher suite
cipher_suite = Fernet(aes_key.encode('utf-8'))

def encrypt_data(data: str) -> str:
    """Menerima string biasa, mengembalikan string terenkripsi."""
    if not data:
        return data
    
    # Fernet membutuhkan data dalam bentuk bytes (encode)
    encrypted_bytes = cipher_suite.encrypt(data.encode('utf-8'))
    # Kembalikan sebagai string agar mudah disimpan ke database
    return encrypted_bytes.decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return encrypted_data
        
    try:
        decrypted_bytes = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        # Menangani jika data gagal didekripsi (misal: kunci berubah atau data corrupt)
        print(f"Error decrypting data: {e}")
        return None