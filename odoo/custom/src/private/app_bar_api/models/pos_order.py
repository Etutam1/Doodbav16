from odoo import models,fields


class PosOrder(models.Model):
    """
    A model representing a Point of Sale (POS) order, extending functionality from the base 'pos.order' model.

    Attributes:
        client_phone (fields.Char): A character field to store the client's phone number. This field is stored in the database.
        notes (fields.Char): A character field to store additional notes related to the POS order. This field is also stored in the database.
    """
    _inherit = "pos.order"
    
    client_phone= fields.Char(string="Teléfono", store=True)
    notes = fields.Char(string="Notas", store=True)
    
    