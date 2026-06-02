import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

class DigitalSignatureService:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def _canonical_json(self, job_data: dict) -> bytes:
        json_string = json.dumps(job_data, sort_keys=True)
        return json_string.encode('utf-8')

    def sign_job_data(self, job_data: dict) -> str:
        data_bytes = self._canonical_json(job_data)
        
        signature = self.private_key.sign(
            data_bytes,
            
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()

    def verify_job_data(self, job_data: dict, signature_hex: str) -> bool:
        data_bytes = self._canonical_json(job_data)
        signature = bytes.fromhex(signature_hex)
        
        try:
            self.public_key.verify(
                signature,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

# Inisialisasi sebagai singleton service
signature_service = DigitalSignatureService()