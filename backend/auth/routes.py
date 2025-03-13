from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from services import (
    generate_access_token,
    generate_refresh_token,
    verify_refresh_token,
    register_user,
    logout_user,
    revoke_refresh_token
)
from models import User, CartItem
from ..models.car import Part
from pydantic import BaseModel

auth_router = APIRouter(prefix="/auth")

# Pydantic-модели
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str

class CartItemSchema(BaseModel):
    user_id: int
    part_id: int
    quantity: int = 1

@auth_router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя."""
    if db.query(User).filter_by(username=user_data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = register_user(user_data.username, user_data.password, db)
    return {"message": "Регистрация успешна", "user_id": user.id}

@auth_router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Авторизация пользователя."""
    user = db.query(User).filter_by(username=user_data.username).first()
    if not user or not user.password:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user, db)
    return {"access_token": access_token, "refresh_token": refresh_token}

@auth_router.post("/refresh")
async def refresh(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Обновление access-токена с помощью refresh-токена."""
    user = verify_refresh_token(token_data.refresh_token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Недействительный refresh-токен")

    access_token = generate_access_token(user)
    return {"access_token": access_token}

@auth_router.post("/logout")
async def logout(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Выход из системы (удаление refresh-токена)."""
    return logout_user(token_data.refresh_token, db)

@auth_router.post("/revoke")
async def revoke(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Отзыв refresh-токена (занесение в черный список)."""
    return revoke_refresh_token(token_data.refresh_token, db)
