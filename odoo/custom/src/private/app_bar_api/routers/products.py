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
    """
Get a list of products.

Returns:
    list[Product2]: A list of products with the following attributes:
        - id (int): The ID of the product.
        - name (str): The name of the product.
        - categ (str): The category of the product.
        - price (float): The price of the product.
        - image (bytes): The image of the product.
        - desc (str): The description of the product.

Raises:
    HTTPException: If no products are available.

"""
    return search_products2(env)


def search_products2(env) -> list[Product2]:
    """
    Searches for products available in the point of sale system and constructs a list of Product2 objects.

    Args:
    env (dict): A dictionary representing the environment context, which includes access to the model 'product.template'.

    Returns:
    list[Product2]: A list of Product2 objects, each representing a product available in the point of sale.

    Raises:
    HTTPException: If no products are found, an HTTPException with status code 204 is raised indicating no products are available.

    Each Product2 object in the returned list contains the following attributes:
    - id (int): The product's unique identifier.
    - name (str): The name of the product.
    - categ (str): The category of the product.
    - price (float): The list price of the product.
    - image (str): A URL or data representing the image of the product.
    - desc (str): A description of the product, suitable for sales.
    """
    result = (env["product.template"].search([("available_in_pos", "=", "true")]).read(["id", "name", "categ_id", "list_price", "image_512", "description_sale"]))

    if not result:
        raise HTTPException(status_code=204, detail="No products available")
    
    return [Product2(
                id=product["id"],
                name=product["name"],
                categ=product["categ_id"][1],
                price=product["list_price"],
                image=get_image(product),
                desc= get_description(product)
            ) for product in result]

def get_description(product):
    """
    Extracts and returns the description from a product dictionary.

    The function checks if the 'description_sale' key in the product dictionary is a string. 
    If it is, it returns this description. If not, it returns an empty string.

    Parameters:
    - product (dict): A dictionary containing product details, expected to have
    a key 'description_sale' with its value as a string representing the description.

    Returns:
    - str: The description of the product. Returns an empty string if 'description_sale' is not
           a string object or is missing.
    """
    desc= ''
    if isinstance(product["description_sale"], str):
        desc= product["description_sale"]
    return desc

def get_image(product):
    """
    Extracts and returns the encoded image from a product dictionary.

    The function checks if the 'image_512' key in the product dictionary contains
    an image encoded as bytes. If it does, it returns this encoded image. If not,
    it returns a default value of bytes([0]).

    Parameters:
    - product (dict): A dictionary containing product details, expected to have
                      a key 'image_512' with its value as bytes representing the image.

    Returns:
    - bytes: The encoded image as bytes. Returns bytes([0]) if 'image_512' is not
             a bytes object or is missing.
    """
    
    encoded_image= bytes([0])
    if isinstance(product["image_512"], bytes):
        encoded_image=product["image_512"]
    return encoded_image
