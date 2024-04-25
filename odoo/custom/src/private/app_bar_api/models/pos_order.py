from odoo import models,fields


class PosOrder(models.Model):
    _inherit = "pos.order"
    
    client_phone= fields.Char(string="Teléfono", store=True)
    notes = fields.Char(string="Notas", store=True)
    
    