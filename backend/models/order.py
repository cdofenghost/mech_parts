from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..models.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, completed, canceled
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="orders")
    cart_items = relationship("CartItem", back_populates="order", cascade="all, delete-orphan")
