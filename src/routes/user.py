from flask import Blueprint, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify({'message': 'Users endpoint', 'status': 'active'})

@user_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'user-service'})
