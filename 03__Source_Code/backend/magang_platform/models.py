# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Pengguna(db.Model):
    __abstract__ = True
    idUser = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Admin(Pengguna):
    __tablename__ = 'admin'
    idAdmin = db.Column(db.String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    lowongan_dikelola = db.relationship('LowonganMagang', backref='admin', lazy=True)

class Mahasiswa(Pengguna):
    __tablename__ = 'mahasiswa'
    nim = db.Column(db.String(20), unique=True, nullable=False)
    programStudi = db.Column(db.String(100), nullable=False)
    lamaran_diajukan = db.relationship('Lamaran', backref='mahasiswa', lazy=True)

class LowonganMagang(db.Model):
    __tablename__ = 'lowongan_magang'
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    dateRange = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.String(50), nullable=True)
    logoUrl = db.Column(db.String(255), nullable=True)
    applyUrl = db.Column(db.String(255), nullable=True)
    workType = db.Column(db.String(50), nullable=False)
    employmentType = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    postedLabel = db.Column(db.String(50), nullable=True)
    about = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.JSON, nullable=True)
    kuota = db.Column(db.Integer, nullable=False)
    idAdmin = db.Column(db.String(50), db.ForeignKey('admin.idAdmin'), nullable=False)
    
    # Kolom untuk menyimpan digital signature (hex string panjang)
    signature = db.Column(db.Text, nullable=True)
    
    # Relationship to Lamaran
    lamaran_masuk = db.relationship('Lamaran', backref='lowongan', lazy=True)
    
    def to_dict(self):
        from services.signature_service import signature_service
        
        status_integritas = "BELUM DITANDATANGANI"
        if self.signature:
            data_to_verify = {
                "id": str(self.id),
                "title": self.title,
                "company": self.company,
                "location": self.location,
                "about": self.about
            }
            is_valid = signature_service.verify_job_data(data_to_verify, self.signature)
            status_integritas = "AMAN / VALID" if is_valid else "PERINGATAN: DATA TELAH DIMANIPULASI!"

        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'dateRange': self.dateRange,
            'type': self.type,
            'location': self.location,
            'salary': self.salary,
            'logoUrl': self.logoUrl or "",
            'applyUrl': self.applyUrl or "",
            'workType': self.workType,
            'employmentType': self.employmentType,
            'duration': self.duration,
            'postedLabel': self.postedLabel,
            'about': self.about,
            'responsibilities': self.responsibilities or [],
            'signature': self.signature or "",
            
            'keamanan_data': status_integritas
        }

class Lamaran(db.Model):
    __tablename__ = 'lamaran'
    idLamaran = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    tanggalApply = db.Column(db.DateTime, default=datetime.utcnow)
    statusLamaran = db.Column(db.String(50), default='Menunggu')
    dokumenCV = db.Column(db.String(255), nullable=False)
    idLowongan = db.Column(db.String(50), db.ForeignKey('lowongan_magang.id'), nullable=False)
    nimMahasiswa = db.Column(db.String(20), db.ForeignKey('mahasiswa.nim'), nullable=False)

class OtpCode(db.Model):
    __tablename__ = 'otp_code'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)

# ✅ MERGE: Pakai nama & struktur AuditLog dari AAA jadi,
#    tambah ip_address_encrypted untuk fitur enkripsi
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.String(50))           
    aksi = db.Column(db.String(255))            
    status = db.Column(db.String(50))
    ipAddress_encrypted = db.Column(db.String)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'endpoint': self.endpoint,
            'activity': self.activity,
            'status': self.status,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            # ip_address tidak di-expose di to_dict; dekripsi dilakukan di service
        }