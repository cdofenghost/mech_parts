from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Связь с таблицей пользователей
    products = Column(String, nullable=False)  # Список VIN/номеров деталей
    status = Column(String, default="В обработке")  # Например: "В обработке", "Отправлено", "Доставлено"
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата создания заказа

    user = relationship("User", back_populates="orders")  # Связь с моделью пользователей