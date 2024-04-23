from pydantic import BaseModel


class Session(BaseModel):
    id: int
    user_id: int
    config_id: int
    sequence_number: int
    login_number: int
