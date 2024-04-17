from typing import Optional, List, Annotated
from fastapi import FastAPI, HTTPException, Depends
import odoo
from odoo.addons.fastapi.dependencies import odoo_env, paging
from odoo.api import Environment
# from ..models.endpoint_inherit import POS_entity as POS
from ..schemas.product import Product, Product2
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from fastapi import APIRouter
import wdb

product_router = APIRouter(tags=["products"])


@product_router.get("/products",
                    response_model=PagedCollection[Product],
                    response_model_exclude_unset=True
                    )
async def get_products(env: Annotated[Environment, Depends(odoo_env)],
                    ) -> PagedCollection[Product]:

    return search_products(env)

def search_products(env) -> PagedCollection[Product]:
    total = env["product.template"].search_count([('available_in_pos', '=', 'true')])
    products = env["product.template"].search([('available_in_pos', '=', 'true')]).read(['id', 'name', 'categ_id', 'list_price'])
    return PagedCollection[Product](count= total, items=[Product.model_validate(product) for product in products])

@product_router.get("/products2",
                    response_model=List[Product2]
                    )
async def get_products2(env: Annotated[Environment, Depends(odoo_env)]) -> List[Product2]:
    return search_products2(env)


def search_products2(env) -> List[Product2]:
    result = env["product.template"].search([('available_in_pos', '=', 'true')]).read(['id', 'name', 'categ_id','list_price'])
    products = []
    for product in result:
        products.append(
            Product2(
                id=product["id"], name=product["name"], categ=product["categ_id"][0], price=product["list_price"]
            )
        )
    return products

@product_router.get("/prueba")
async def get_prueba() -> bool:
    wdb.set_trace()
    return True
