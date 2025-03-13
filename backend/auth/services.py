import jwt
import datetime
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User, RefreshToken, RevokedToken
from ..database import SessionLocal
from fastapi import Depends

SECRET_KEY = "mysecret"  # Можно вынести в .env

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_access_token(user: User):
    """Генерирует JWT-токен доступа."""
    return jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

def generate_refresh_token(user: User, db: Session):
    """Генерирует refresh-токен, удаляет старый и сохраняет новый в базе."""
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()

    refresh_token = str(uuid.uuid4())
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)

    new_refresh_token = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(new_refresh_token)
    db.commit()

    return refresh_token

def verify_refresh_token(refresh_token: str, db: Session):
    """Проверяет refresh-токен и возвращает пользователя, если он действителен."""
    if db.query(RevokedToken).filter_by(token=refresh_token).first():
        return None

    token_record = db.query(RefreshToken).filter_by(token=refresh_token).first()
    if token_record and token_record.expires_at > datetime.datetime.utcnow():
        return db.query(User).get(token_record.user_id)

    return None

def register_user(username: str, password: str, db: Session):
    """Регистрирует нового пользователя."""
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def logout_user(refresh_token: str, db: Session):
    """Выход пользователя (удаляет refresh-токен)."""
    db.query(RefreshToken).filter_by(token=refresh_token).delete()
    db.commit()
    return {"message": "Выход выполнен, токен удален"}

def revoke_refresh_token(refresh_token: str, db: Session):
    """Добавляет токен в черный список (отзывает токен)."""
    revoked_token = RevokedToken(token=refresh_token, revoked_at=datetime.datetime.utcnow())
    db.add(revoked_token)
    db.commit()
    return {"message": "Токен отозван"}
