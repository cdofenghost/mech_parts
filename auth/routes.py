from flask import Blueprint, request, jsonify
from auth.services import generate_access_token, generate_refresh_token, verify_refresh_token, register_user
from auth.models import User
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Пользователь уже существует'}), 400
    user = register_user(username, password)
    return jsonify({'message': 'Регистрация успешна'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Авторизация пользователя."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
    return jsonify({'message': 'Неверные учетные данные'}), 401

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Обновление access-токена с помощью refresh-токена."""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    user = verify_refresh_token(refresh_token)
    if user:
        access_token = generate_access_token(user)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Недействительный refresh-токен'}), 401
