import urllib.request
import json

# --- 1. SETTING AKUN ADMIN KAMU DI SINI ---
EMAIL_ADMIN = "andra@gmail.com"  # Ganti dengan email admin di databasemu
PASSWORD_ADMIN = "123"  # Ganti dengan password adminmu

def run_test():
    print("Mencoba login...")
    
    # Menyiapkan data login
    login_data = json.dumps({"email": EMAIL_ADMIN, "password": PASSWORD_ADMIN}).encode('utf-8')
    req_login = urllib.request.Request(
        "http://localhost:5001/login", 
        data=login_data, 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        # Melakukan Request Login
        response = urllib.request.urlopen(req_login)
        response_data = json.loads(response.read().decode('utf-8'))
        
        token = response_data.get("access_token")
        if not token:
            print("Gagal mendapat token. Pastikan email dan password benar!")
            return
            
        print("Login berhasil! Token didapatkan.\n")
        print("Mengambil data log dari server...\n")
        
        # 2. Mengambil data log menggunakan Token
        req_logs = urllib.request.Request(
            "http://localhost:5001/admin/logs", 
            headers={'Authorization': f'Bearer {token}'}
        )
        
        logs_response = urllib.request.urlopen(req_logs)
        logs_data = json.loads(logs_response.read().decode('utf-8'))
        
        # 3. Menampilkan Hasil
        print("="*50)
        print("HASIL DEKRIPSI IP DARI BACKEND FLASK")
        print("="*50)
        
        if len(logs_data) == 0:
            print("Belum ada data log di database.")
        else:
            for log in logs_data:
                print(f"User   : {log.get('idUser', 'Unknown')}")
                print(f"Status : {log.get('status')}")
                print(f"IP Asli: {log.get('ipAddress')}  <-- (Ini adalah hasil dekripsi!)")
                print(f"Waktu  : {log.get('waktu')}")
                print("-" * 30)
                
    except Exception as e:
        print(f"Terjadi error: {e}")
        print("Pastikan server Docker kamu sedang menyala dan email/password benar.")

if __name__ == "__main__":
    run_test()