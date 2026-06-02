from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.magang_controller import MagangController

magang_bp = Blueprint('magang', __name__)

# Public: Mencari Lowongan
magang_bp.route('/lowongan', methods=['GET'])(MagangController.get_all_lowongan)
magang_bp.route('/lowongan/<id>', methods=['GET'])(MagangController.get_detail_lowongan)

# Mahasiswa: Melamar & Tracking Dashboard
magang_bp.route('/lamaran', methods=['POST'])(jwt_required()(MagangController.apply_lowongan))
magang_bp.route('/mahasiswa/dashboard', methods=['GET'])(jwt_required()(MagangController.get_dashboard))
magang_bp.route('/lamaran/<id>/status', methods=['PUT'])(jwt_required()(MagangController.update_lamaran_status))
magang_bp.route('/lamaran/<id>', methods=['DELETE'])(jwt_required()(MagangController.delete_lamaran))