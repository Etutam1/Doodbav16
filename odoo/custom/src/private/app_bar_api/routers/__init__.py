from fastapi import APIRouter
from .products import product_router

router = APIRouter()
router.include_router(product_router)
