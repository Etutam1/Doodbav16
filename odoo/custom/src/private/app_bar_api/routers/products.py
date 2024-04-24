from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from ..schemas.product import Product, Product2
import wdb

product_router = APIRouter(tags=["products"], responses={404: {"message": "Not Found"}})


@product_router.get(
    "/products",
    response_model=list[Product],
    response_model_exclude_unset=True,
    status_code=200,
)
async def get_products(
    env: Annotated[Environment, Depends(odoo_env)],
) -> list[Product]:
    """
    Get a list of products.

    Parameters:
    - env: Annotated[Environment, Depends(odoo_env)] - The Odoo environment.

    Returns:
    - list[Product]: A list of products.

    Raises:
    - HTTPException: If no products are available.

    """
    return search_products(env)


def search_products(env) -> list[Product]:
    """
    Searches for products in the Odoo environment.

    Parameters:
    - env: An instance of the Odoo environment.

    Returns:
    - A list of Product objects containing the searched products.

    Raises:
    - HTTPException with status code 204 if no products are available.

    Example Usage:
    search_products(env)
    """
    products = (env["product.template"].search([("available_in_pos", "=", "true")]).read(["id", "name", "categ_id", "list_price"], None))
    if not products:
        raise HTTPException(status_code=204, detail="No products available")
    return [Product.model_validate(product) for product in products]


@product_router.get("/products2", response_model=list[Product2], status_code=200)
async def get_products2(
    env: Annotated[Environment, Depends(odoo_env)]
) -> list[Product2]:
    return search_products2(env)


def search_products2(env) -> list[Product2]:
    result = (
        env["product.template"]
        .search([("available_in_pos", "=", "true")])
        .read(["id", "name", "categ_id", "list_price", "image_512", "description_sale"])
    )

    if not result:
        raise HTTPException(status_code=204, detail="No products available")
    
    products = []
    # wdb.set_trace()
    for product in result:
        
        encoded_image= bytes([0])
        if isinstance(product["image_512"], bytes):
            encoded_image=product["image_512"]
            
        products.append(
            Product2(
                id=product["id"],
                name=product["name"],
                categ=product["categ_id"][1],
                price=product["list_price"],
                image=encoded_image,
                # desc= product["description_sale"]
            )
        )
    
    return products


@product_router.get("/prueba")
async def get_prueba() -> bool:
    return True
