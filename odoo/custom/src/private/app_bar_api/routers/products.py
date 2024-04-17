from fastapi import APIRouter, Depends

from odoo.addons.fastapi.dependencies import odoo_env

# from ..models.endpoint_inherit import POS_entity as POS
from ..schemas.product import Product

product_router = APIRouter(tags=["products"])


def search_products(env):
    result = env["product.template"]
    products = []
    for record in result:
        if record.get("purchase_ok"):
            products.append(
                Product(
                    id=record["id"], name=record["name"], categ_id=record["categ_id"].id
                )
            )
    return products if products else {"Error: No products found"}


@product_router.get("/products", response_model=list[Product])
async def get_products(env: dict = Depends(odoo_env)):
    return search_products(env)
