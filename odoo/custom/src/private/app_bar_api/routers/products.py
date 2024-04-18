from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi.schemas import PagedCollection

from ..schemas.product import Product, Product2

product_router = APIRouter(
    tags=["products"],
    responses={404: {"message: Not Found"}},
)


@product_router.get(
    "/products",
    response_model=PagedCollection[Product],
    response_model_exclude_unset=True,
    status_code=201,
)
async def get_products(
    env: Annotated[Environment, Depends(odoo_env)],
) -> PagedCollection[Product]:
    return search_products(env)


def search_products(env) -> PagedCollection[Product]:
    total = env["product.template"].search_count([("available_in_pos", "=", "true")])
    products = (
        env["product.template"]
        .search([("available_in_pos", "=", "true")])
        .read(["id", "name", "categ_id", "list_price"])
    )
    if not products:
        raise HTTPException(status_code=204, detail="No products available")
    return PagedCollection[Product](
        count=total, items=[Product.model_validate(product) for product in products]
    )


@product_router.get("/products2", response_model=list[Product2])
async def get_products2(
    env: Annotated[Environment, Depends(odoo_env)]
) -> list[Product2]:
    return search_products2(env)


def search_products2(env) -> list[Product2]:
    result = (
        env["product.template"]
        .search([("available_in_pos", "=", "true")])
        .read(["id", "name", "categ_id", "list_price"])
    )
    products = []
    for product in result:
        products.append(
            Product2(
                id=product["id"],
                name=product["name"],
                categ=product["categ_id"][0],
                price=product["list_price"],
            )
        )
    return products


@product_router.get("/prueba")
async def get_prueba() -> bool:
    return True
