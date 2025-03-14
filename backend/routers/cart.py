from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.order import Order
from ..models.cart import CartItem
from ..auth.models import User
from ..schemas.cart import CartItemCreate, CartItemResponse
from ..models.car import Part
from datetime import datetime
from ..auth.services import get_current_user  # Импорт проверки токена

cart_router = APIRouter(prefix="/cart")


@cart_router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
    cart_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавление товара в корзину с привязкой к заказу."""
    part = db.query(Part).filter(Part.id == cart_data.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Запчасть не найдена")

    order = db.query(Order).filter(Order.user_id == current_user.id, Order.status == "pending").first()
    if not order:
        order = Order(user_id=current_user.id, status="pending", created_at=datetime.utcnow())
        db.add(order)
        db.commit()
        db.refresh(order)

    cart_item = db.query(CartItem).filter(CartItem.order_id == order.id, CartItem.part_id == cart_data.part_id).first()

    if cart_item:
        cart_item.quantity += cart_data.quantity
    else:
        cart_item = CartItem(order_id=order.id, part_id=cart_data.part_id, quantity=cart_data.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


@cart_router.get("/", response_model=list[CartItemResponse])
async def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Проверка токена
):
    """Получение содержимого корзины активного заказа пользователя."""
    order = db.query(Order).filter(Order.user_id == current_user.id, Order.status == "pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Нет активного заказа")

    return db.query(CartItem).filter(CartItem.order_id == order.id).all()


@cart_router.delete("/remove")
async def remove_from_cart(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Проверка токена
):
    """Удаление конкретного товара из активного заказа."""
    order = db.query(Order).filter(Order.user_id == current_user.id, Order.status == "pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Нет активного заказа")

    cart_item = db.query(CartItem).filter(CartItem.order_id == order.id, CartItem.part_id == part_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар в корзине не найден")

    db.delete(cart_item)
    db.commit()

    # Если корзина пустая - удаляем заказ
    remaining_items = db.query(CartItem).filter(CartItem.order_id == order.id).count()
    if remaining_items == 0:
        db.delete(order)
        db.commit()

    return {"message": "Товар удален из корзины"}


@cart_router.delete("/clear")
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Очистка всей корзины (удаление всех товаров из активного заказа)."""
    order = db.query(Order).filter(Order.user_id == current_user.id, Order.status == "pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Нет активного заказа")

    db.query(CartItem).filter(CartItem.order_id == order.id).delete()
    db.commit()
    return {"message": "Корзина очищена"}
