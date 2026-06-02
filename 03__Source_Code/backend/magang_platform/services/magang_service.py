from models import db, LowonganMagang, Lamaran

class MagangService:
    @staticmethod
    def create_lowongan(data, admin_id):
        new_lowongan = LowonganMagang(
            title=data.get('title'),
            company=data.get('company'),
            dateRange=data.get('dateRange'),
            type=data.get('type'),
            location=data.get('location'),
            salary=data.get('salary'),
            logoUrl=data.get('logoUrl', ''),
            applyUrl=data.get('applyUrl', ''),
            workType=data.get('workType'),
            employmentType=data.get('employmentType'),
            duration=data.get('duration'),
            postedLabel=data.get('postedLabel'),
            about=data.get('about'),
            responsibilities=data.get('responsibilities', []),
            kuota=data.get('kuota', 1), # Backend specific
            idAdmin=admin_id
        )
        db.session.add(new_lowongan)
        db.session.commit()
        return new_lowongan

    @staticmethod
    def update_lowongan(id_lowongan, data):
        lowongan = LowonganMagang.query.get(id_lowongan)
        if not lowongan:
            return None
        
        # Update matching fields dynamically
        for key, value in data.items():
            if hasattr(lowongan, key) and key not in ['id', 'idAdmin']:
                setattr(lowongan, key, value)

        db.session.commit()
        return lowongan

    @staticmethod
    def delete_lowongan(id_lowongan):
        lowongan = LowonganMagang.query.get(id_lowongan)
        if not lowongan:
            return False
        db.session.delete(lowongan)
        db.session.commit()
        return True

    @staticmethod
    def get_lowongan(keyword=None, type_filter=None):
        query = LowonganMagang.query
        if keyword:
            query = query.filter(
                LowonganMagang.title.ilike(f'%{keyword}%') | 
                LowonganMagang.company.ilike(f'%{keyword}%')
            )
        if type_filter:
            query = query.filter_by(type=type_filter)
        return query.all()
    
    @staticmethod
    def get_lowongan_by_id(id_lowongan):
        return LowonganMagang.query.get(id_lowongan)

    @staticmethod
    def create_lamaran(data, nim_mahasiswa):
        new_lamaran = Lamaran(
            dokumenCV=data['dokumenCV'],
            idLowongan=data['idLowongan'],
            nimMahasiswa=nim_mahasiswa
        )
        db.session.add(new_lamaran)
        db.session.commit()
        return new_lamaran

    @staticmethod
    def get_lamaran_by_mahasiswa(nim_mahasiswa):
        return Lamaran.query.filter_by(nimMahasiswa=nim_mahasiswa).all()

    @staticmethod
    def update_status_lamaran(id_lamaran, nim_mahasiswa, status):
        lamaran = Lamaran.query.get(id_lamaran)
        if not lamaran:
            return None, "Lamaran tidak ditemukan"
        if lamaran.nimMahasiswa != nim_mahasiswa:
            return None, "Anda tidak memiliki akses ke lamaran ini"
            
        lamaran.statusLamaran = status
        db.session.commit()
        return lamaran, None
    
    @staticmethod
    def delete_lamaran(id_lamaran, nim_mahasiswa):
        lamaran = Lamaran.query.get(id_lamaran)
        if not lamaran:
            return False, "Lamaran tidak ditemukan"
        if lamaran.nimMahasiswa != nim_mahasiswa:
            return False, "Anda tidak memiliki akses untuk menghapus lamaran ini"
            
        db.session.delete(lamaran)
        db.session.commit()
        return True, None