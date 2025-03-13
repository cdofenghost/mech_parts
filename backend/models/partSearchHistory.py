from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class PartSearchHistory(Base):
    __tablename__ = "part_search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ID пользователя, сделавшего запрос
    part_name = Column(String, nullable=False)  # Название запчасти
    search_count = Column(Integer, default=1)  # Количество поисков этой запчасти

    def __repr__(self):
        return f"<PartSearchHistory(user_id={self.user_id}, part_name={self.part_name}, search_count={self.search_count})>"
