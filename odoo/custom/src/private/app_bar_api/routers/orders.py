from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas.session import Session

order_router = APIRouter(tags=["orders"])

# @order_router.post('order/create', status_code=201)
# async def create_order(env: Annotated[Environment, Depends(odoo_env)]):
# return True


@order_router.get("/current_session", status_code=200, response_model=Session)
async def current_session(env: Annotated[Environment, Depends(odoo_env)]) -> Session:
    return get_session_data(env)


def get_session_data(env):
    session = (
        env["pos.session"]
        .sudo()
        .search(["|", ("state", "=", "opened"), ("state", "=", "opening_control")])
        .read(["id", "user_id", "config_id"])
    )

    if not session:
        raise HTTPException(status_code=204, detail="Not open session found")
    # try:
    #     return Session.model_validate(session[0])
    # except ValueError as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@order_router.post("/create_order", status_code=201)
async def create_order(env: Annotated[Environment, Depends(odoo_env)]):
    session_data = get_session_data(env)
    datetime = get_formated_datetime()
    order = env["pos.order"]
    # orderLine = env["pos.order.line"]

    new_order = order.sudo().create(
        [
            {
                "company_id": 1,
                "pricelist_id": 1,
                "session_id": session_data.id,
                "name": "Pruebas/0002",
                "pos_reference": "Pedido 00003-008-0004",
                "amount_tax": 0.00,
                "amount_total": 12.0,
                "amount_paid": 12.0,
                "amount_return": 0.00,
                "date_order": datetime,
                "create_date": datetime,
                "write_date": datetime,
            }
        ]
    )

    # for line in order_data.lines:
    #     OrderLine.create({
    #         'order_id': new_order.id,
    #         'product_id': line.product_id,
    #         'quantity': line.quantity,
    #         # add other necessary fields as per your model
    #     })

    return {"message": "Order created successfully", "order_id": new_order.id}


def get_formated_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
