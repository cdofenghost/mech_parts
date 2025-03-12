import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash
from auth.models import User, RefreshToken, db
from flask import current_app

def generate_access_token(user):
    """Генерирует JWT-токен доступа."""
    return jwt.encode({
        'user': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

def generate_refresh_token(user):
    """Генерирует refresh-токен и сохраняет его в базе."""
    refresh_token = str(uuid.uuid4())
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    new_refresh_token = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.session.add(new_refresh_token)
    db.session.commit()
    return refresh_token

def verify_refresh_token(refresh_token):
    """Проверяет refresh-токен и возвращает пользователя, если он действителен."""
    token_record = RefreshToken.query.filter_by(token=refresh_token).first()
    if token_record and token_record.expires_at > datetime.datetime.utcnow():
        return User.query.get(token_record.user_id)
    return None

def register_user(username, password):
    """Регистрирует нового пользователя."""
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user
