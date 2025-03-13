from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from models.partSearchHistory import PartSearchHistory
from models.order import Order

class Base(DeclarativeBase):
    pass

DATABASE_URL = "postgresql://postgres:dofenbase@localhost:5432/MechaBase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_orders():
    """Получает список всех заказов."""
    with SessionLocal() as db:
        result = db.execute(select(Order).order_by(Order.created_at.desc()))
        return result.scalars().all()

def init_db():
    """Создает таблицы в базе данных."""
    Base.metadata.create_all(bind=engine)

def get_frequent_parts(limit=10):
    """Получает список самых популярных запчастей."""
    with SessionLocal() as db:
        result = db.execute(select(PartSearchHistory.part_name).order_by(PartSearchHistory.search_count.desc()).limit(limit))
        return [row[0] for row in result.fetchall()]

def get_user_search_history(user_id):
    """Получает историю поиска запчастей пользователя."""
    with SessionLocal() as db:
        result = db.execute(select(PartSearchHistory.part_name).where(PartSearchHistory.user_id == user_id))
        return [row[0] for row in result.fetchall()]
