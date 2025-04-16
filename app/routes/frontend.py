from flask import Blueprint, send_from_directory

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
@frontend_bp.route('/<path:path>')
def serve_user_frontend(path='index.html'):
    return send_from_directory('static/user', path)
