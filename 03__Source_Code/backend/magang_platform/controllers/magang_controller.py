from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from services.magang_service import MagangService
from validators.validator import validate_lowongan_data
from services.signature_service import signature_service
from models import db
from services.auth_service import AuthService  # ✅ Tambah import ini

class MagangController:
    # --- ADMIN ROUTES ---
    @staticmethod
    def add_lowongan():
        claims = get_jwt()
        user_id = get_jwt_identity()
        role = claims.get('role')
        ip_addr = request.remote_addr

        # ✅ AUTHORIZATION + ACCOUNTING: Catat jika bukan admin
        if role != 'admin':
            AuthService.log_activity(
                user_id=user_id,
                role=role,
                endpoint=request.path,
                activity="Mencoba menambah lowongan baru tanpa hak akses (Authorization Failed)",
                status="FAILED",
                ip_address=ip_addr
            )
            return jsonify({"message": "Akses ditolak, khusus admin"}), 403

        data = request.json
        is_valid, msg = validate_lowongan_data(data)
        if not is_valid:
            return jsonify({"message": msg}), 400

        lowongan = MagangService.create_lowongan(data, get_jwt_identity())
        # LOGIKA DIGITAL SIGNATURE UNTUK ADD JOB NEW
        try:
            data_to_sign = {
                "id": lowongan.id,
                "title": lowongan.title,
                "company": lowongan.company,
                "location": lowongan.location,
                "about": lowongan.about
            }
            new_signature = signature_service.sign_job_data(data_to_sign)
            lowongan.signature = new_signature
            db.session.commit() # Kunci signature baru ke database
            
            return jsonify({
                "message": "Lowongan berhasil ditambahkan dan ditandatangani secara digital", 
                "id": lowongan.id,
                "signature": new_signature
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Gagal membuat lowongan karena issue signature: {str(e)}"}), 500
        lowongan = MagangService.create_lowongan(data, user_id)

        # ✅ ACCOUNTING: Catat sukses tambah lowongan
        AuthService.log_activity(
            user_id=user_id,
            role=role,
            endpoint='/admin/lowongan',
            activity=f"Berhasil menambahkan lowongan baru ID: {lowongan.id}",
            status='SUCCESS',
            ip_address=ip_addr
        )

        return jsonify({
            "message": "Lowongan berhasil ditambahkan",
            "id": lowongan.id
        }), 201

    @staticmethod
    def update_lowongan(id):
        if get_jwt().get('role') != 'admin':
            return jsonify({"message": "Akses ditolak, khusus admin"}), 403

        lowongan = MagangService.update_lowongan(id, request.json)
        if not lowongan:
            return jsonify({"message": "Lowongan tidak ditemukan"}), 404
        
        # LOGIKA DIGITAL SIGNATURE UNTUK EDIT JOB
        try:
            # 1. Kumpulkan field penting dari objek lowongan yang sudah ter-update
            data_to_sign = {
                "id": lowongan.id,
                "title": lowongan.title,
                "company": lowongan.company,
                "location": lowongan.location,
                "about": lowongan.about
            }
            
            # 2. Generate signature dari dictionary di atas
            new_signature = signature_service.sign_job_data(data_to_sign)
            
            # 3. Tempel hasil signature ke kolom model lowongan
            lowongan.signature = new_signature
            
            # 4. Save/Commit perubahan signature secara aman ke database
            db.session.commit()
            
            return jsonify({
                "message": "Lowongan berhasil diupdate dan ditandatangani secara digital",
                "signature": new_signature
            }), 200
            
        except Exception as e:
            # Jika ada masalah pada kriptografinya, database rollback agar data tetap konsisten
            db.session.rollback()
            return jsonify({"message": f"Gagal generate digital signature: {str(e)}"}), 500

    @staticmethod
    def delete_lowongan(id):
        if get_jwt().get('role') != 'admin':
            return jsonify({"message": "Akses ditolak, khusus admin"}), 403

        success = MagangService.delete_lowongan(id)
        if not success:
            return jsonify({"message": "Lowongan tidak ditemukan"}), 404
        return jsonify({"message": "Lowongan berhasil dihapus"}), 200

    # --- PUBLIC/MAHASISWA ROUTES ---
    @staticmethod
    def get_all_lowongan():
        hasil = MagangService.get_lowongan(request.args.get('keyword'), request.args.get('type'))
        return jsonify([l.to_dict() for l in hasil]), 200

    @staticmethod
    def get_detail_lowongan(id):
        l = MagangService.get_lowongan_by_id(id)
        if not l:
            return jsonify({"message": "Lowongan tidak ditemukan"}), 404
        return jsonify(l.to_dict()), 200

    @staticmethod
    def apply_lowongan():
        if get_jwt().get('role') != 'mahasiswa':
            return jsonify({"message": "Hanya mahasiswa yang dapat mengirim lamaran"}), 403

        data = request.json
        lamaran = MagangService.create_lamaran(data, get_jwt_identity())
        return jsonify({"message": "Lamaran berhasil dikirim", "idLamaran": lamaran.idLamaran}), 201

    @staticmethod
    def get_dashboard():
        if get_jwt().get('role') != 'mahasiswa':
            return jsonify({"message": "Akses ditolak"}), 403

        lamaran = MagangService.get_lamaran_by_mahasiswa(get_jwt_identity())
        if not lamaran:
            return jsonify({"message": "Dashboard kosong"}), 200
            
        return jsonify([{
            "idLamaran": l.idLamaran,
            "idLowongan": l.idLowongan,
            "title": l.lowongan.title,
            "company": l.lowongan.company,
            "tanggalApply": l.tanggalApply.strftime('%Y-%m-%d %H:%M:%S'),
            "statusLamaran": l.statusLamaran
        } for l in lamaran]), 200

    @staticmethod
    def update_lamaran_status(id):
        if get_jwt().get('role') != 'mahasiswa':
            return jsonify({"message": "Akses ditolak"}), 403

        lamaran, error = MagangService.update_status_lamaran(id, get_jwt_identity(), request.json.get('statusLamaran'))
        if error:
            return jsonify({"message": error}), 400
        return jsonify({"message": "Status lamaran berhasil diperbarui"}), 200

    @staticmethod
    def delete_lamaran(id):
        if get_jwt().get('role') != 'mahasiswa':
            return jsonify({"message": "Akses ditolak"}), 403

        success, error = MagangService.delete_lamaran(id, get_jwt_identity())
        if error:
            return jsonify({"message": error}), 404 if "ditemukan" in error else 403
        return jsonify({"message": "Lamaran berhasil dihapus"}), 200