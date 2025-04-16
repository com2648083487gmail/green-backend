from flask import Blueprint, send_from_directory

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('/<path:path>')
def serve_admin_frontend(path='index.html'):
    return send_from_directory('static/admin', path)
