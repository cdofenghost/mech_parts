from fastapi import APIRouter

router = APIRouter(prefix="/search")

@router.post("/car_info_by_vin")
async def search_car_info_by_vin():
    pass

@router.post("/part_info_by_number")
async def search_part_info_by_number():
    pass

@router.post("/part_list_by_vin")
async def search_part_list_by_vin():
    pass

@router.post("/interchangables_by_number")
async def search_interchangables_by_number():
    pass