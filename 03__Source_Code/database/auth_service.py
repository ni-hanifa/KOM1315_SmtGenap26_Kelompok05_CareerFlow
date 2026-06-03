from models import db, Admin, Mahasiswa, OtpCode, ActivityLog
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import random
import string
from datetime import datetime, timedelta, timezone
from utils.crypto import encrypt_data, decrypt_data  # ✅ Enkripsi tetap ada


class AuthService:
    @staticmethod
    def create_mahasiswa(data):
        if Mahasiswa.query.filter_by(email=data['email']).first() or Mahasiswa.query.filter_by(nim=data['nim']).first():
            return None, "Email atau NIM sudah terdaftar"
        
        hashed_password = generate_password_hash(data['password'])
        new_mahasiswa = Mahasiswa(
            nama=data['nama'],
            email=data['email'],
            password=hashed_password,
            nim=data['nim'],
            programStudi=data['programStudi']
        )
        db.session.add(new_mahasiswa)
        db.session.commit()
        return new_mahasiswa, None

    @staticmethod
    def authenticate_user(email, password):
        # ✅ Signature kembali seperti AAA jadi (tanpa ip_address parameter)
        # IP dihandle di controller seperti AAA jadi
        user = Admin.query.filter_by(email=email).first()
        role = 'admin'
        user_id = user.idAdmin if user else None

        if not user:
            user = Mahasiswa.query.filter_by(email=email).first()
            role = 'mahasiswa'
            user_id = user.nim if user else None

        if not user:
            return None, None, "Email atau password salah"

        if role == 'admin':
            if user.password != password:
                return None, None, "Email atau password salah"
        else:
            if not check_password_hash(user.password, password):
                return None, None, "Email atau password salah"

        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={'role': role}
        )
        return access_token, role, None

    @staticmethod
    def generate_otp(email, purpose):
        if purpose == 'signup' and Mahasiswa.query.filter_by(email=email).first():
            return None, "Email sudah terdaftar"
        
        if purpose == 'forgot' and not Mahasiswa.query.filter_by(email=email).first():
            return None, "Email tidak ditemukan"

        otp = ''.join(random.choices(string.digits, k=6))
        OtpCode.query.filter_by(email=email, purpose=purpose, is_used=False).update({'is_used': True})
        
        db.session.add(OtpCode(email=email, otp=otp, purpose=purpose))
        db.session.commit()
        print(f"OTP for {email} ({purpose}): {otp}")
        return otp, None

    @staticmethod
    def verify_otp(email, otp, purpose):
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        code = OtpCode.query.filter_by(email=email, otp=otp, purpose=purpose, is_used=False).order_by(OtpCode.created_at.desc()).first()
        
        if not code or (now_naive - code.created_at > timedelta(minutes=10)):
            return False, "OTP salah atau kadaluarsa"
        
        if purpose == 'signup':
            code.is_used = True
            db.session.commit()
            
        return True, None

    @staticmethod
    def reset_password(email, otp, new_password):
        is_valid, msg = AuthService.verify_otp(email, otp, 'forgot')
        if not is_valid:
            return False, msg

        user = Mahasiswa.query.filter_by(email=email).first()
        if not user:
            return False, "Email tidak ditemukan"

        user.password = generate_password_hash(new_password)
        
        code = OtpCode.query.filter_by(email=email, otp=otp, purpose='forgot', is_used=False).order_by(OtpCode.created_at.desc()).first()
        if code:
            code.is_used = True
            
        db.session.commit()
        return True, None

    @staticmethod
    def get_user_profile(user_id, role):
        if role == 'admin':
            user = Admin.query.get(user_id)
            return {"name": getattr(user, 'nama', 'Admin'), "role": "Admin"} if user else None
            
        elif role == 'mahasiswa':
            user = Mahasiswa.query.filter_by(nim=user_id).first()
            return {"name": getattr(user, 'nama', 'Mahasiswa'), "role": "Mahasiswa"} if user else None
            
        return None

    @staticmethod
    def update_user_profile(user_id, role, data, password=None):
        if role == 'admin':
            user = Admin.query.get(user_id)
        elif role == 'mahasiswa':
            user = Mahasiswa.query.filter_by(nim=user_id).first()
        else:
            return None, "Role tidak valid"
        if not user:
            return None, "User tidak ditemukan"

        if 'email' in data and data['email'] != user.email:
            if not password or not check_password_hash(user.password, password):
                return None, "Password salah untuk konfirmasi email"
            if Admin.query.filter_by(email=data['email']).first() or Mahasiswa.query.filter_by(email=data['email']).first():
                return None, "Email sudah digunakan"
            user.email = data['email']

        if 'nama' in data:
            user.nama = data['nama']
        if 'username' in data and hasattr(user, 'username'):
            user.username = data['username']
        if 'bio' in data and hasattr(user, 'bio'):
            user.bio = data['bio']
        if 'photo' in data and hasattr(user, 'photo'):
            user.photo = data['photo']

        db.session.commit()
        return AuthService.get_user_profile(user_id, role), None

    @staticmethod
    def log_activity(user_id, role, endpoint, activity, status, ip_address=None):
        try:
            # Enkripsi IP sebelum disimpan ke database
            encrypted_ip = encrypt_data(ip_address or "0.0.0.0")

            # KEMBALI MENGGUNAKAN ActivityLog
            # Parameter role dan endpoint kita gabungkan ke dalam 'aksi' agar tidak hilang
            log_entry = ActivityLog(
                idUser=str(user_id) if user_id else 'anonymous',
                aksi=f"[{role.upper()}] {endpoint} - {activity}", 
                status=status,
                ipAddress_encrypted=encrypted_ip  # <-- Kembali pakai A besar
            )
            db.session.add(log_entry)
            db.session.commit()
            print(f"[ACTIVITY] {status} | {role} | {endpoint} | {activity}")
        except Exception as e:
            db.session.rollback()
            print(f"[ACTIVITY ERROR] {str(e)}")
            raise

    @staticmethod
    def get_all_logs():
        # KEMBALI MENGGUNAKAN ActivityLog
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
        hasil_log = []

        for log in logs:
            # Dekripsi IP sebelum dikirim ke frontend
            ip_asli = decrypt_data(log.ipAddress_encrypted) if log.ipAddress_encrypted else None

            hasil_log.append({
                "id": log.id,
                "idUser": log.idUser,
                "aksi": log.aksi,
                "status": log.status,
                "ipAddress": ip_asli,  # IP sudah terdekripsi
                "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return hasil_log