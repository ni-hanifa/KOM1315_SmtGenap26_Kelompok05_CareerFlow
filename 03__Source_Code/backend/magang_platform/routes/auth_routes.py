from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

# Sign Up & Login (Added 'OPTIONS' to both)
auth_bp.route('/signup', methods=['POST', 'OPTIONS'])(AuthController.signup)
auth_bp.route('/login', methods=['POST', 'OPTIONS'])(AuthController.login)

# OTP Send & Verify (Added 'OPTIONS' to both)
auth_bp.route('/signup/send-otp', methods=['POST', 'OPTIONS'])(AuthController.send_signup_otp)
auth_bp.route('/signup/verify-otp', methods=['POST', 'OPTIONS'])(AuthController.verify_signup_otp)

# Forgot Password (Added 'OPTIONS' to all)
auth_bp.route('/forgot-password/send-otp', methods=['POST', 'OPTIONS'])(AuthController.send_forgot_otp)
auth_bp.route('/forgot-password/verify-otp', methods=['POST', 'OPTIONS'])(AuthController.verify_forgot_otp)
auth_bp.route('/forgot-password/reset', methods=['POST', 'OPTIONS'])(AuthController.reset_password)

# Profile (Added 'OPTIONS' to both GET and PUT)
auth_bp.route('/profile', methods=['GET', 'OPTIONS'])(jwt_required()(AuthController.get_profile))
auth_bp.route('/profile', methods=['PUT', 'OPTIONS'])(jwt_required()(AuthController.update_profile))