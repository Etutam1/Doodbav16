from pydantic import BaseModel

from .product import ProductLine


class Order(BaseModel):
    products: list[ProductLine]
    total: float
    client_phone: str
    date_order: str
    notes: str
