from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from ..schemas.order import Order
from ..schemas.session import Session
from pydantic import ValidationError
order_router = APIRouter(tags=["orders"])


@order_router.get("/current_session", status_code=200, response_model=Session)
async def current_session(env: Annotated[Environment, Depends(odoo_env)]) -> Session:
    """
    Get the current session.

    This function retrieves the current session from the Odoo environment and returns it as a response. 
    The session is obtained by calling the `get_session` function, passing the `env` parameter.

    Parameters:
    - env (Environment): The Odoo environment.

    Returns:
    - Session: The current session.

    Raises:
    - HTTPException: If no open session is found or if there is an error validating the session.

    """
    return get_session(env)
      
def get_session(env):
    """
    Retrieves the current open or opening control session from the environment.

    This function searches for sessions that are either in the 'opened' or 'opening_control' state.
    It reads specific fields from the found session records. If no session is found, it raises an HTTPException
    with a status code of 204 indicating no open session was found. If the session data fails validation,
    it raises an HTTPException with a status code of 500 and provides the error detail.

    Parameters:
    - env (dict): The environment dictionary containing session information and methods.

    Returns:
    - Session: A validated session object.
    """
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
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@order_router.post("/create_order", status_code=201)
async def create_order(env: Annotated[Environment, Depends(odoo_env)], order_data: Order):
    """
    Create a new order.

    Parameters:
    - env: Annotated[Environment, Depends(odoo_env)] - The Odoo environment.
    - order_data: Order - The order data.

    Returns:
    - dict - A dictionary containing the message and the order reference.

    Raises:
    - HTTPException(400) - If the order data is invalid or if the order creation fails.
    - HTTPException(500) - If there is an unexpected error during the order creation.
    """
    
    try:
        
        pos_session = get_session(env)
         
        # if not Order.validate_model(order_data):
        #     raise ValidationError('Invalid order data')
        
        new_order = insert_order(env, pos_session, order_data)
        
        if not new_order:
            raise HTTPException(status_code=400, detail="Failed to create order")
        
        insert_lines(env, order_data, new_order)
            
        return {"message": "Order created successfully", "order_reference": new_order.pos_reference}
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid order data: {str(e)}")
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"Failed to create order: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
    

def insert_order(env, session, order):
    """
    Inserts an order into the Point of Sale (POS) system.

    This function takes in the environment dictionary and an order object as parameters. 
    It performs the following steps:

    1. Generates a unique reference for the order using the '_generate_unique_ref' function.
    2. Calculates the sequence number for the order using the 'calculate_sequence_number' function.
    3. Retrieves the Point of Sale (POS) information for the session using the 'get_pos_info' function.
    4. Formats the current datetime using the 'get_formated_datetime' function.
    5. Creates a new order in the POS system using the 'pos.order' model and the provided data.

    Parameters:
    - env (dict): The environment dictionary containing session information and methods.
    - session(Session): The current open or opening control session from the environment.
    - order (Order): The order object containing the order details.

    Returns:
    - int: The ID of the newly created order in the POS system.
    """
    sequence = env["ir.sequence"].next_by_code("pos.order.pruebas")
    session.sequence_number = calculate_sequence_number(env, session)
    current_datetime = get_formated_datetime()
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
                    "create_date": current_datetime,
                    "write_date": current_datetime,
                    "x_client_phone": order.client_phone,
                    "x_notes": order.notes,
                }
            ]
        )
    )
    

def insert_lines(env, order_data, new_order):
    """
    Inserts order lines into the Point of Sale (POS) system.

    This function takes in the environment dictionary, order data, and the newly created order as parameters. 
    It performs the following steps:

    1. Iterates over each product in the order data.
    2. Generates a unique sequence number for each order line using the 'ir.sequence' model.
    3. Creates a new order line in the POS system using the 'pos.order.line' model and the provided data.

    Parameters:
    - env (dict): The environment dictionary containing session information and methods.
    - order_data (Order): The order data containing the product details.
    - new_order (int): The ID of the newly created order in the POS system.

    Raises:
    - HTTPException(400): If the order line creation fails.

    """
    for line in order_data.products:
        sequence_number = env["ir.sequence"].next_by_code("pos.order.line.pruebas")
        
        order_line = {
                "product_id": line.product_id,
                "order_id": new_order.id,
                "name": sequence_number,
                "full_product_name": line.name,
                "price_unit": line.price_unit,
                "qty": line.qty,
                "price_subtotal": line.price_subtotal,
                "price_subtotal_incl": line.price_subtotal_incl,
                "create_date": new_order.create_date,
                "write_date": new_order.write_date,
            }
        
        if not env["pos.order.line"].create([order_line]):
            raise HTTPException(status_code=400, detail=f"Failed to insert order line")

def _generate_unique_ref(session):
    """
    Generates a unique reference for an order.

    This function takes in a session object as a parameter and generates a unique reference for an order. 
    The reference is generated by concatenating the session ID, login number, and the incremented sequence number. The session ID 
    is zero-padded to a size of 5, the login number is zero-padded to a size of 3, and the sequence number is incremented by 1 
    and zero-padded to a size of 4.

    Parameters:
    - session: The session object containing the session ID, login number, and sequence number.

    Returns:
    - str: The unique reference for the order.
    """
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
    """
    Retrieve Point of Sale (POS) information.

    This function takes in the environment dictionary and a POS ID as parameters. It performs the following steps:

    1. Searches for a POS configuration record in the environment using the provided POS ID.
    2. Reads specific fields from the found POS configuration record, including the pricelist ID and company ID.

    Parameters:
    - env (dict): The environment dictionary containing session information and methods.
    - pos_id (str): The ID of the POS configuration to retrieve information for.

    Returns:
    - dict: A dictionary containing the pricelist ID and company ID of the POS configuration.
    """
    return (
        env["pos.config"]
        .sudo()
        .search([("id", "=", pos_id)], limit=1)
        .read(["pricelist_id", "company_id"], None)[0]
    )


def calculate_sequence_number(env, current_session) -> int:
    """
    Calculate the sequence number for a new order.

    This function takes in the environment dictionary and the current session as parameters. It performs the following steps:

    1. Retrieves the most recent order's POS reference from the 'pos.order' model.
    2. Parses the POS reference to extract the session ID, login number, and sequence number.
    3. Compares the extracted session ID and login number with the current session's ID and login number.
    4. If the session ID and login number match, returns the sequence number.
    5. If the session ID or login number does not match, returns 0, reseting the sequence.

    Parameters:
    - env (dict): The environment dictionary containing session information and methods.
    - current_session: The current session object containing the session ID and login number.

    Returns:
    - int: The calculated sequence number for a new order.
    """
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
    """
    Returns the current datetime in a formatted string.

    This function uses the `datetime.now()` function from the `datetime` module to get the current datetime.
    It then formats the datetime using the `strftime()` method, with the format string "%Y-%m-%d %H:%M:%S".
    The format string represents the year, month, day, hour, minute, and second in a specific order.

    Returns:
        str: The current datetime in the format "YYYY-MM-DD HH:MM:SS".
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")



