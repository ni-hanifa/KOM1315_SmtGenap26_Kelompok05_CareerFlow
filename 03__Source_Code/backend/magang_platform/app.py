# app.py
from flask import Flask
from models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.magang_routes import magang_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
    # Configure CORS to allow requests from your React frontend
    CORS(
    app,
    resources={r"/*": {"origins": [FRONTEND_URL, "http://localhost:3001"]}},
    supports_credentials=True
    )

    # Tambahkan konfigurasi database dan JWT dari environment variables
    # Buat file .env di root project dengan isi:
    # DATABASE_URL=postgresql://username:password@localhost:5432/nama_database
    # JWT_SECRET_KEY=string_rahasia_untuk_jwt
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Tambahkan Secret Key untuk JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    # Setup Database
    db.init_app(app)
    jwt = JWTManager(app) # Inisialisasi JWT

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(magang_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)