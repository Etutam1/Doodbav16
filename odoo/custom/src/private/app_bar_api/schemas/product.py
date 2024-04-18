from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    categ_id: tuple
    list_price: float


class Product2(BaseModel):
    id: int
    name: str
    categ: int
    price: float
