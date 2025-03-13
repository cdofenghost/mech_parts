from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.cart import CartItem
from ..models.user import User
from ..schemas.cart import CartItemCreate, CartItemResponse
from ..models.car import Part

cart_router = APIRouter(prefix="/cart")

@cart_router.post("/add", response_model=CartItemResponse)
async def add_to_cart(cart_data: CartItemCreate, user_id: int, db: Session = Depends(get_db)):
    """Добавление товара в корзину."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    part = db.query(Part).filter(Part.id == cart_data.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Запчасть не найдена")

    cart_item = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.part_id == cart_data.part_id).first()

    if cart_item:
        cart_item.quantity += cart_data.quantity
    else:
        cart_item = CartItem(user_id=user_id, part_id=cart_data.part_id, quantity=cart_data.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item

@cart_router.get("/{user_id}", response_model=list[CartItemResponse])
async def get_cart(user_id: int, db: Session = Depends(get_db)):
    """Получение содержимого корзины пользователя."""
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()

@cart_router.delete("/remove")
async def remove_from_cart(user_id: int, part_id: int, db: Session = Depends(get_db)):
    """Удаление конкретного товара из корзины."""
    cart_item = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.part_id == part_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар в корзине не найден")

    db.delete(cart_item)
    db.commit()
    return {"message": "Товар удален из корзины"}

@cart_router.delete("/clear/{user_id}")
async def clear_cart(user_id: int, db: Session = Depends(get_db)):
    """Очистка всей корзины пользователя."""
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    return {"message": "Корзина очищена"}
