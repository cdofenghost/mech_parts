from pydantic import BaseModel

class CartItemCreate(BaseModel):
    part_id: int
    quantity: int

class CartItemResponse(CartItemCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
