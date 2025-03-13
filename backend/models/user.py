from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base  # Импортируем базовый класс из database.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)

    orders = relationship("Order", back_populates="user")  # Связь с заказами
