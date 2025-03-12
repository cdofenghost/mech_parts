from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session

import requests

from ..database import get_db
from ..models.car import Car
from ..schemas.car import CarIn
from ..utils.urls import BASE_URL, USER, PW
from ..utils.token_generator import generate_token

router = APIRouter(prefix="/methods")

def create_db_car(car_in: CarIn) -> Car:
    db_car = Car(**car_in.model_dump())
    return db_car

@router.post("/get_car_info")
async def get_car_info(vin: str = Body(embed=True), db: Session = Depends(get_db)):
    '''
    https://www.17vin.com/doc.html. Раздел 3001.\n
    Выдает информацию о модели машину по заданному VIN.
    '''
    token = "c2181f8363ad0d0ef892c611140244e2"

    existing_car = db.query(Car).filter(Car.vin_id == vin).first()

    if existing_car:
        return existing_car
    
    # TO-DO: Сгенерировать создание токена по VIN'у
    url = f"{BASE_URL}/?vin={vin}&user={USER}&token={token}"
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

    if code != 1:
        return {"message": f"С таким VIN результатов не найдено. Код результата: {code}"}
    
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
    epc = model_list["Epc"]
    epc_id = model_list["Epc_id"]
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

    car_in = CarIn(
        vin_id=vin,
        model_year_from_vin=model_year_from_vin,
        model_year=model_year,
        made_in=made_in,
        brand=brand,
        model_detail=model_detail,
        epc=epc,
        epc_id=epc_id,
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
    )
    db_car = create_db_car(car_in)    

    db.add(db_car)
    db.commit()

    return part_data

@router.post("/get_parts_info")
async def get_parts_info(epc: str = Body(embed=True), query_part_number: str = Body(embed=True)):
    '''
    https://www.17vin.com/doc.html. Раздел 4002.\n
    Поиск в списке категорий.
    ???
    '''
    url_parameters = f"/{epc}?action=search_illustration&query_part_number={query_part_number}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)
    print(f"{token=},{url_parameters=}")
    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    print(url)
    
    # Выполняем GET-запрос к API VIN17
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_part_by_qpn")
async def get_part_by_qpn(query_part_number: str = Body(embed=True), query_match_type: str = Body(embed=True, default="smart")):
    '''
    https://www.17vin.com/doc.html. Раздел 4001.\n
    Выдает запчасть по ее номеру запчасти/аксессуара - <b>query_part_number.</b>\n
    <b>query_match_type</b> - необязательно. Означает тип поиска, принимает строки 3 видов:\n
        "exact" - строгий поиск\n
        "inexact" - нестрогий поиск\n
        "smart" (default) - умный поиск (сначала строгий поиск; если не найдено - нестрогий).\n
    ''' 
    url_parameters = f"/?action=search_epc&query_part_number={query_part_number}&query_match_type={query_match_type}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_interchange")
async def get_interchange_by_pn_and_group_id(part_number: str = Body(embed=True), group_id: str = Body(embed=True)):
    '''
    Раздел 4004.\n
    Получить номер замены через номер акссесуара/запчасти (номер детали бренда).
    '''
    url_parameters = f"/?action=get_interchange_from_part_number_and_group_id_plus_zh&part_number={part_number}&group_id={group_id}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_accessories_list")
async def get_accessories_list_by_catalog_code(epc: str = Body(embed=True), cata_code: str = Body(embed=True)):
    '''
    Раздел 4005.\n
    '''
    url_parameters = f"/{epc}?action=illustration&cata_code={cata_code}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_parts_info")
async def get_parts_info_by_brand_and_qpn(brand: str = Body(embed=True), 
                                          query_part_number: str = Body(embed=True), 
                                          query_match_type: str = Body(embed=True, default="smart")):
    '''
    Раздел 40071.
    '''

    url_parameters = f"/?action=aftermarket_private_part_search&manufacturer_brand={brand}&query_part_number={query_part_number}&query_match_type={query_match_type}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

# не реализовал 40031, 40032, 4006, 40073