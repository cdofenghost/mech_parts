from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import requests
import logging

from ..database import get_db
from ..models.car import Car
from ..schemas.car import CarIn
from ..utils.urls import BASE_URL

router = APIRouter(prefix="/car_info")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_car(car_in: CarIn) -> Car:
    db_car = Car(**car_in.model_dump())
    return db_car

@router.get("/{vin}/{user}/{token}")
async def get_car_info(vin: str, user: str, token: str, db: Session = Depends(get_db)):
    # Формируем URL для запроса
    url = f"{BASE_URL}/?vin={vin}&user={user}&token={token}"
    print(url)
    
    # Выполняем GET-запрос к API VIN17
    response = requests.get(url)
    
    # Проверяем статус ответа
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    # First Level
    code = part_data["code"]
    msg = part_data["msg"]
    data = part_data["data"]

    # Data Level
    vin = data["full_vin"]
    model_year_from_vin = data["model_year_from_vin"]
    made_in = data["made_in_en"]
    model_list = data["model_list"][0]

    # Model List Level
    model_year = model_list["Model_year"]
    model_detail = model_list["Model_detail_en"]
    factory = model_list["Factory_en"]
    brand = model_list["Brand_en"]
    series = model_list["Series_en"]
    model = model_list["Model_en"]
    sales_version = model_list["Sales_version_en"]
    capacity = model_list["Cc_en"]
    engine_no = model_list["Engine_no_en"]
    kilowatt = model_list["Kw"]
    horse_power = model_list["Hp"]
    air_intake = model_list["Air_intake_en"]
    fuel_type = model_list["Fuel_type_en"]
    transmission_detail = model_list["Transmission_detail_en"]
    gear_num = model_list["Gear_num_en"]
    driving_mode = model_list["Driving_mode_en"]
    door_num = model_list["Door_num_en"]
    seat_num = model_list["Seat_num"]
    body_type = model_list["Body_type_en"]
    price = model_list["Price"]
    price_unit = model_list["Price_unit"]

    db_car = create_db_car(CarIn(
        vin_id=vin,
        model_year_from_vin=model_year_from_vin,
        model_year=model_year,
        made_in=made_in,
        brand=brand,
        model_detail=model_detail,
        factory=factory,
        series=series,
        model=model,
        sales_version=sales_version,
        capacity=capacity,
        engine_no=engine_no,
        kilowatt=kilowatt,
        horse_power=horse_power,
        air_intake=air_intake,
        fuel_type=fuel_type,
        transmission_detail=transmission_detail,
        gear_num=gear_num,
        driving_mode=driving_mode,
        door_num=door_num,
        seat_num=seat_num,
        body_type=body_type,
        price=price,
        price_unit=price_unit
    ))    

    db.add(db_car)
    db.commit()

    return part_data