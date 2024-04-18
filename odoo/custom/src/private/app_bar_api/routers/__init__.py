from . import orders
from . import products
from fastapi import APIRouter
from .products import product_router
from .orders import order_router

router = APIRouter()
router.include_router(product_router)
router.include_router(order_router)
