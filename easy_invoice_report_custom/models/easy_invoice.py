from odoo import fields, models


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

    product_uom_qty = fields.Float(string='invoiced amount', store=True)
    delivered_qty = fields.Float(string='delivered quantity', store=True)