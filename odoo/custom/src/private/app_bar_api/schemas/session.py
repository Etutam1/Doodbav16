from pydantic import BaseModel


class Session(BaseModel):
    id: int
    user_id: list
    config_id: list
