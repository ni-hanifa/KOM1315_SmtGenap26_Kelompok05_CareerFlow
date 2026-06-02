from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.magang_controller import MagangController
from controllers.auth_controller import AuthController

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Mengelola Lowongan (The /admin prefix is applied automatically)
admin_bp.route('/lowongan', methods=['POST'])(jwt_required()(MagangController.add_lowongan))
admin_bp.route('/lowongan/<id>', methods=['PUT'])(jwt_required()(MagangController.update_lowongan))
admin_bp.route('/lowongan/<id>', methods=['DELETE'])(jwt_required()(MagangController.delete_lowongan))
admin_bp.route('/logs', methods=['GET', 'OPTIONS'])(jwt_required()(AuthController.get_activity_logs))