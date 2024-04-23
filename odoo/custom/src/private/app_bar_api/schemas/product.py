from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    categ_id: int
    list_price: float


class Product2(BaseModel):
    id: int
    name: str
    categ: str
    price: float


class ProductLine(BaseModel):
    product_id: int
    name: str
    price_unit: float
    qty: int
    price_subtotal: float
    price_subtotal_incl: float
