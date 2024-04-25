from fastapi import APIRouter

from odoo import fields, models

from ..routers import router


class FastapiEndpoint(models.Model):
    """
    A model class that represents a FastAPI endpoint, inheriting from a base model.

    Attributes:
        app (str): A field that selects the type of application this endpoint is associated with.
                   It allows addition of new types via `selection_add` and handles deletion
                   of associated data through the `ondelete` parameter.

    Inheritance:
        Inherits from "fastapi.endpoint" which should be a predefined model in the system.
    """
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("POS_entity", "POS Entities")],
        ondelete={"POS_entity": "cascade"},
    )

    def _get_fastapi_routers(self) -> list[APIRouter]:
        """
        Retrieves a list of FastAPI routers associated with the endpoint based on the `app` attribute.

        Returns:
            list[APIRouter]: A list containing the APIRouter instances associated with this endpoint.
                             If `app` is set to "POS_entity", it returns a predefined list `[router]`.
                             Otherwise, it calls the superclass method to get the routers.
        """
        if self.app == "POS_entity":
            return [router]
        return super()._get_fastapi_routers()
