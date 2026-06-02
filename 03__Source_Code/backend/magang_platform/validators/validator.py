def validate_required_fields(data, required_fields):
    """Fungsi helper untuk mengecek field yang wajib ada"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Field berikut wajib diisi: {', '.join(missing_fields)}"
    return True, ""

def validate_signup_data(data):
    required = ['nama', 'email', 'password', 'nim', 'programStudi']
    return validate_required_fields(data, required)

def validate_lowongan_data(data):
    # Updated to match the new model attributes that are nullable=False
    required = [
        'title', 
        'company', 
        'dateRange', 
        'type', 
        'location', 
        'workType', 
        'employmentType', 
        'duration', 
        'about', 
        'kuota'
    ]
    return validate_required_fields(data, required)


# Profile update validator
def validate_profile_update_data(data):
    # You can adjust required fields as needed (e.g., allow partial updates)
    required = ['nama', 'email']
    return validate_required_fields(data, required)