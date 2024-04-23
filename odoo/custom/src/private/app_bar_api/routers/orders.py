from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas.order import Order
from ..schemas.session import Session

order_router = APIRouter(tags=["orders"])

# @order_router.post('order/create', status_code=201)
# async def create_order(env: Annotated[Environment, Depends(odoo_env)]):
# return True


@order_router.get("/current_session", status_code=200, response_model=Session)
async def current_session(env: Annotated[Environment, Depends(odoo_env)]) -> Session:
    return get_session(env)


def get_session(env):
    session = (
        env["pos.session"]
        .sudo()
        .search(["|", ("state", "=", "opened"), ("state", "=", "opening_control")])
        .read(["id", "user_id", "config_id", "sequence_number", "login_number"], None)
    )

    if not session:
        raise HTTPException(status_code=204, detail="Not open session found")
    try:
        return Session.model_validate(session[0])
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@order_router.post("/create_order", status_code=201)
async def create_order(
    env: Annotated[Environment, Depends(odoo_env)], order_data: Order
):
    new_order = insert_order(env, order_data)

    for line in order_data.products:
        sequence_line = env["ir.sequence"].next_by_code("pos.order.line.pruebas")
        env["pos.order.line"].create(
            [
                {
                    "product_id": line.product_id,
                    "order_id": new_order.id,
                    "name": sequence_line,
                    "full_product_name": line.name,
                    "price_unit": line.price_unit,
                    "qty": line.qty,
                    "price_subtotal": line.price_subtotal,
                    "price_subtotal_incl": line.price_subtotal_incl,
                    "create_date": new_order.create_date,
                    "write_date": new_order.write_date,
                }
            ]
        )

    # sale_line = self.env['sale.order.line'].create({
    #                 'order_id': sale_order_origin.id,
    #                 'product_id': line.product_id.id,
    #                 'price_unit': line.price_unit,
    #                 'product_uom_qty': 0,
    #                 'tax_id': [(6, 0, line.tax_ids.ids)],
    #                 'is_downpayment': True,
    #                 'discount': line.discount,
    #                 'sequence': sale_lines and sale_lines[-1].sequence + 1 or 10,
    #             })

    return {"message": "Order created successfully", "order_id": new_order.id}


def _generate_unique_ref(session):
    def zero_pad(num, size):
        s: str = str(num)
        while len(s) < size:
            s = "0" + s
        return s

    return (
        zero_pad(session.id, 5)
        + "-"
        + zero_pad(session.login_number, 3)
        + "-"
        + zero_pad(session.sequence_number + 1, 4)
    )


def get_pos_info(env, pos_id: str):
    return (
        env["pos.config"]
        .sudo()
        .search([("id", "=", pos_id)], limit=1)
        .read(["pricelist_id", "company_id"], None)[0]
    )


def calculate_sequence_number(env, current_session) -> int:
    ref = (
        env["pos.order"]
        .sudo()
        .search([], order="create_date desc", limit=1)
        .read(["pos_reference"], None)[0]["pos_reference"]
    )

    if ref:
        session_id = int(
            "".join(
                number
                for number in list(ref.split("-")[0].split(" ")[1])
                if number != "0"
            )
        )
        login_number = int(
            "".join(number for number in list(ref.split("-")[1]) if number != "0")
        )
        seq = int(
            "".join(number for number in list(ref.split("-")[2]) if number != "0")
        )

        if (
            current_session.id != session_id
            or current_session.login_number != login_number
        ):
            return 0
        else:
            return seq


def get_formated_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def insert_order(env, order):
    session = get_session(env)
    sequence = env["ir.sequence"].next_by_code("pos.order.pruebas")
    session.sequence_number = calculate_sequence_number(env, session)
    datetime = get_formated_datetime()
    pos_info = get_pos_info(env, session.config_id)
    ref = _generate_unique_ref(session)
    return (
        env["pos.order"]
        .sudo()
        .create(
            [
                {
                    "company_id": pos_info["company_id"],
                    "pricelist_id": pos_info["pricelist_id"],
                    "session_id": session.id,
                    "name": sequence,
                    "pos_reference": "Pedido " + ref,
                    "amount_tax": 0.00,
                    "amount_total": order.total,
                    "amount_paid": order.total,
                    "amount_return": 0.00,
                    "date_order": order.date_order,
                    "create_date": datetime,
                    "write_date": datetime,
                    "x_client_phone": order.client_phone,
                    "x_notes": order.notes,
                }
            ]
        )
    )
