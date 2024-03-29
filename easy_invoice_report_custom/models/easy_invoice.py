from odoo import fields, models


class EasyInvoiceLine(models.Model):
    _inherit = "easy.invoice.line"

    product_uom_qty = fields.Float(string='invoiced amount')
    delivered_qty = fields.Float(string='delivered quantity')