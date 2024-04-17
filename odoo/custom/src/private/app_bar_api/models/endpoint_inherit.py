from fastapi import APIRouter

from odoo import fields, models

from ..routers import router

# POS_entity = APIRouter()


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("POS_entity", "POS Entities")],
        ondelete={"POS_entity": "cascade"},
    )

    def _get_fastapi_routers(self) -> list[APIRouter]:
        if self.app == "POS_entity":
            return [router]
        return super()._get_fastapi_routers()
