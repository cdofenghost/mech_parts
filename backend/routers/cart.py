from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.order import Order
from ..models.cart import CartItem
from ..models.user import User
from ..schemas.cart import CartItemCreate, CartItemResponse
from ..models.car import Part
from datetime import datetime

cart_router = APIRouter(prefix="/cart")

@cart_router.post("/add", response_model=CartItemResponse)
async def add_to_cart(cart_data: CartItemCreate, user_id: int, db: Session = Depends(get_db)):
    """Добавление товара в корзину с привязкой к заказу."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    part = db.query(Part).filter(Part.id == cart_data.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Запчасть не найдена")

    # Получаем текущий "незавершенный" заказ или создаем новый
    order = db.query(Order).filter(Order.user_id == user_id, Order.status == "pending").first()
    if not order:
        order = Order(user_id=user_id, status="pending", created_at=datetime.utcnow())
        db.add(order)
        db.commit()
        db.refresh(order)

    # Проверяем, есть ли уже этот товар в заказе
    cart_item = db.query(CartItem).filter(CartItem.order_id == order.id, CartItem.part_id == cart_data.part_id).first()

    if cart_item:
        cart_item.quantity += cart_data.quantity
    else:
        cart_item = CartItem(order_id=order.id, part_id=cart_data.part_id, quantity=cart_data.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item

@cart_router.get("/{user_id}", response_model=list[CartItemResponse])
async def get_cart(user_id: int, db: Session = Depends(get_db)):
    """Получение содержимого корзины активного заказа пользователя."""
    order = db.query(Order).filter(Order.user_id == user_id, Order.status == "pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Нет активного заказа")

    return db.query(CartItem).filter(CartItem.order_id == order.id).all()

@cart_router.delete("/remove")
async def remove_from_cart(user_id: int, part_id: int, db: Session = Depends(get_db)):
    """Удаление конкретного товара из активного заказа."""
    order = db.query(Order).filter(Order.user_id == user_id, Order.status == "pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Нет активного заказа")

    cart_item = db.query(CartItem).filter(CartItem.order_id == order.id, CartItem.part_id == part_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар в корзине не найден")

    db.delete(cart_item)
    db.commit()

    # 🔥 Если корзина пустая - удаляем заказ
    remaining_items = db.query(CartItem).filter(CartItem.order_id == order.id).count()
    if remaining_items == 0:
        db.delete(order)
        db.commit()

    return {"message": "Товар удален из корзины"}



@cart_router.delete("/clear/{user_id}")
async def clear_cart(user_id: int, db: Session = Depends(get_db)):
    """Очистка всей корзины (удаление всех товаров из активного заказа)."""
    order = db.query(Order).filter(Order.user_id == user_id, Order.status == "pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Нет активного заказа")

    db.query(CartItem).filter(CartItem.order_id == order.id).delete()
    db.commit()
    return {"message": "Корзина очищена"}
