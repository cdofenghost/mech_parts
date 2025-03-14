import jwt
import datetime
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User, RefreshToken, RevokedToken
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security, HTTPException, Depends

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли пароль с хэшем"""
    return pwd_context.verify(plain_password, hashed_password)

def generate_access_token(user: User):
    """Генерирует access token"""
    return jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm=ALGORITHM)

def generate_refresh_token(user: User, db: Session):
    """Генерирует refresh token, удаляет старый и сохраняет новый"""
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()

    refresh_token = str(uuid.uuid4())
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)

    new_refresh_token = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(new_refresh_token)
    db.commit()

    return refresh_token

def verify_refresh_token(refresh_token: str, db: Session):
    """Проверяет refresh token и возвращает пользователя, если он действителен"""
    if db.query(RevokedToken).filter_by(token=refresh_token).first():
        return None

    token_record = db.query(RefreshToken).filter_by(token=refresh_token).first()
    if token_record and token_record.expires_at > datetime.datetime.utcnow():
        return db.query(User).filter(User.id == token_record.user_id).first()

    return None

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    """Декодирует JWT и возвращает текущего пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            print("Неверный токен")
            raise HTTPException(status_code=401, detail="Неверный токен")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            print("Пользователь не найден")
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user
    
    except jwt.ExpiredSignatureError:
        print("Токен истек")
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.InvalidTokenError:
        print("Недействительный токен")
        raise HTTPException(status_code=401, detail="Недействительный токен")

def register_user(username: str, password: str, db: Session):
    """Регистрирует нового пользователя"""
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def logout_user(refresh_token: str, db: Session):
    """Удаляет refresh token"""
    db.query(RefreshToken).filter_by(token=refresh_token).delete()
    db.commit()
    return {"message": "Выход выполнен"}

def revoke_refresh_token(refresh_token: str, db: Session):
    """Добавляет refresh token в черный список"""
    revoked_token = RevokedToken(token=refresh_token, revoked_at=datetime.datetime.utcnow())
    db.add(revoked_token)
    db.commit()
    return {"message": "Токен отозван"}
