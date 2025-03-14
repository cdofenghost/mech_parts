from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    part_id = Column(Integer, ForeignKey("parts.id"))
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="cart_items")
    part = relationship("Part", back_populates="cart_items")

