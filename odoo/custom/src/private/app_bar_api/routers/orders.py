from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas.session import Session

order_router = APIRouter(tags=["orders"])

# @order_router.post('order/create', status_code=201)
# async def create_order(env: Annotated[Environment, Depends(odoo_env)]):
#     return True


@order_router.get("/current_session", status_code=200, response_model=Session)
async def current_session(env: Annotated[Environment, Depends(odoo_env)]) -> Session:
    session = (
        env["pos.session"]
        .search([("state", "=", "opening_control")])
        .read(["id", "user_id"])
    )
    if not session:
        raise HTTPException(status_code=204, detail="Not open session found")
    try:
        return Session.model_validate(session[0])
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
