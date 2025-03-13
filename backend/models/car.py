from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand_name = Column(String)
    group_id = Column(String)
    part_number = Column(String)

class Car(Base):
    __tablename__ = "cars"

    vin_id = Column(String, primary_key=True, index=True)
    part_number_list = Column(String)
    model_year_from_vin = Column(String)
    model_year = Column(String)
    made_in = Column(String)
    model_detail = Column(String)
    epc = Column(String)
    epc_id = Column(String)
    brand = Column(String)
    factory = Column(String)
    series = Column(String)
    model = Column(String)
    sales_version = Column(String)
    capacity = Column(String)
    engine_no = Column(String)
    kilowatt = Column(String)
    horse_power = Column(String)
    air_intake = Column(String)
    fuel_type = Column(String)
    transmission_detail = Column(String)
    gear_num = Column(String)
    driving_mode = Column(String)
    door_num = Column(String)
    seat_num = Column(String)
    body_type = Column(String)
    price = Column(String)
    price_unit = Column(String)

class PartSearchHistory(Base):
    __tablename__ = "part_search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ID пользователя, сделавшего запрос
    part_name = Column(String, nullable=False)  # Название запчасти
    search_count = Column(Integer, default=1)  # Количество поисков этой запчасти

    def __repr__(self):
        return f"<PartSearchHistory(user_id={self.user_id}, part_name={self.part_name}, search_count={self.search_count})>"