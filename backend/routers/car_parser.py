from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session

import requests

from ..database import get_db
from ..models.car import Car, Part
from ..schemas.car import CarIn, PartIn
from ..utils.urls import BASE_URL, USER, PW, IMG_URL
from ..utils.token_generator import generate_token

router = APIRouter(prefix="/search")

def create_db_car(car_in: CarIn) -> Car:
    db_car = Car(**car_in.model_dump())
    return db_car

def create_db_part(part_in: PartIn) -> Part:
    db_part = Part(name=part_in.name,
                   epc=part_in.epc,
                   brand_name=part_in.brand_name,
                   group_id=part_in.group_id,
                   part_number=part_in.part_number,
                   img_src=part_in.img_src)
    return db_part

def request_image(img_src: str):
    response = requests.get(f"{IMG_URL}/{img_src}")

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="what")
    
    return response.json()

def request_car_info(vin: str):
    '''
    https://www.17vin.com/doc.html. Раздел 3001.\n
    Выдает информацию о модели машину по заданному VIN.
    '''
    url_parameters = f"/?vin={vin}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
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

    return db_car

def request_part_info(query_part_number: str, query_match_type: str):
    url_parameters = f"/?action=search_epc&query_part_number={query_part_number}&query_match_type={query_match_type}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()
    parts = part_data["data"]

    result = []
    for part in parts:
        part_in = PartIn(name=part["Part_name_en"],
                         epc=part["Epc_en"],
                         brand_name=part["Brand_name_en"],
                         group_id=part["Group_id"],
                         part_number=part["Partnumber"],
                         img_src=part["Part_img"],
                         )
        result.append(part_in)
        
    return result
        
        

@router.post("/car_info_by_vin", tags=["Главное"]) #3001 (ПОИСК ДАННЫХ О МАШИНЕ ПО VIN)
async def search_car_info(vin: str = Body(embed=True), db: Session = Depends(get_db)):

    existing_car = db.query(Car).filter(Car.vin_id == vin).first()

    if existing_car:
        return existing_car
    
    db_car = request_car_info(vin)

    db.add(db_car)
    db.commit()

    return db_car

@router.post("/part_info_by_number", tags=["Главное"]) #4001 (ПОИСК ПО НОМЕРУ)
async def search_part_info_by_number(query_part_number: str = Body(embed=True), 
                          query_match_type: str = Body(embed=True, default="smart"),
                          db: Session = Depends(get_db)):
    '''
    https://www.17vin.com/doc.html. Раздел 4001.\n
 
    Выдает запчасть по ее номеру запчасти/аксессуара - <b>query_part_number.</b>\n
    <b>query_match_type</b> - необязательно. Означает тип поиска, принимает строки 3 видов:\n
        "exact" - строгий поиск\n
        "inexact" - нестрогий поиск\n
        "smart" (default) - умный поиск (сначала строгий поиск; если не найдено - нестрогий).\n
    ''' 
    existing_part = db.query(Part).filter(Part.part_number == query_part_number).first()
    
    if existing_part:
        return existing_part
    
    parts = request_part_info(query_part_number, query_match_type)

    for part_in in parts:
        db_part = create_db_part(part_in)
        db.add(db_part)
        db.commit()

    return parts[0]

@router.post("/interchangables_by_number_and_group_id", tags=["Главное"]) #4004
async def search_interchangables_by_pn_and_group_id(part_number: str = Body(embed=True), 
                                                    group_id: str = Body(embed=True)):
    '''
    Раздел 4004.\n
    Тест кейс: part_number=6RD615301 group_id=2\n
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

@router.post("/get_parts_info", tags=["Пункт 4"]) #4002
async def get_parts_info(epc: str = Body(embed=True), query_part_number: str = Body(embed=True)):
    '''
    https://www.17vin.com/doc.html. Раздел 4002.\n
    Поиск в списке категорий.\n
    Тест кейс: epc=toyota query_part_number=091140G010
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

    return part_data["data"]

@router.post("/get_accessories_list_from_catalogue", tags=["Пункт 4"]) # 4005
async def get_accessories_list_by_catalogue_code(epc: str = Body(embed=True), cata_code: str = Body(embed=True)):
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

@router.post("/get_parts_info_by_qpn", tags=["Пункт 4"]) # 40071
async def get_parts_info_by_brand_and_qpn(brand: str = Body(embed=True), 
                                          query_part_number: str = Body(embed=True), 
                                          query_match_type: str = Body(embed=True, default="smart")):
    '''
    Раздел 40071.\n
    Тест кейс: manufacturer_brand=Jingshi Information Technology Co., Ltd. query_part_number=JSB00001&query_match_type=smart\n
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

@router.post("/get_all_part_numbers", tags=["Пункт 5"]) # 5109
async def get_all_part_numbers_from_vin(epc: str = Body(embed=True), 
                                        vin: str = Body(embed=True)):
    '''
    Раздел 5109.\n
    Тестовый запрос: http://api.17vin.com:8080/toyota?action=all_part_number&vin=LFMGJE720DS070251&user=international_dofenspot&token=442fc8ce6e38fcbc1f74f92e4be5a9fa
    '''
    url_parameters = f"/{epc}?action=all_part_number&vin={vin}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    numbers = part_data["data"].split("@")

    return {"numbers": numbers}

@router.post("/get_catalogue_1", tags=["Пункт 5", "Каталоги"]) # 5101
async def get_catalogue_level_1(epc: str = Body(embed=True),
                                vin: str = Body(embed=True)):
    url_parameters = f"/{epc}?action=cata1&vin={vin}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_catalogue_2", tags=["Пункт 5", "Каталоги"]) # 5102
async def get_catalogue_level_2(epc: str = Body(embed=True), 
                                vin: str = Body(embed=True), 
                                cata1_code: str = Body(embed=True)):
    
    url_parameters = f"/{epc}?action=cata2&vin={vin}&cata1_code={cata1_code}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_catalogue_3", tags=["Пункт 5", "Каталоги"]) # 5103
async def get_catalogue_level_3(epc: str = Body(embed=True), 
                                vin: str = Body(embed=True), 
                                cata2_code: str = Body(embed=True)):
    
    url_parameters = f"/{epc}?action=cata3&vin={vin}&cata2_code={cata2_code}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_catalogue_4", tags=["Пункт 5", "Каталоги"]) # 5104
async def get_catalogue_level_4(epc: str = Body(embed=True), 
                                vin: str = Body(embed=True), 
                                cata3_code: str = Body(embed=True)):
    
    url_parameters = f"/{epc}?action=cata4&vin={vin}&cata3_code={cata3_code}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_accessories_list")
async def get_accessories_list(epc: str = Body(embed=True), 
                               vin: str = Body(embed=True), 
                               last_cata_code: str = Body(embed=True),
                               last_cata_code_level: str = Body()):
    
    url_parameters = f"/{epc}?action=part&vin={vin}&last_cata_code={last_cata_code}&last_cata_code_level={last_cata_code_level}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data

@router.post("/get_spare_parts_by_vin", tags=["Пункт 7"]) # 7001
async def get_spare_parts_by_vin(vin: str = Body(embed=True),
                                 brand: str = Body(embed=True),
                                 category: str = Body(embed=True)):
    '''
    Раздел 7001. Поиск запчастей по VIN-коду.
    Тест кейс: vin=LFMGJE720DS070251 manufacturer_brand=Bosch category=Filter
    '''
    url_parameters = f"/?action=aftermarket_vin&vin={vin}&manufacturer_brand={brand}&category={category}"
    token = generate_token(username=USER, password=PW, url_parameters=url_parameters)

    url = f"{BASE_URL}{url_parameters}&user={USER}&token={token}"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе данных")
    
    # Преобразуем ответ в JSON
    part_data = response.json()

    return part_data