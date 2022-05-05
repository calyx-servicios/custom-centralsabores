from odoo import fields, models


class EasyInvoiceLine(models.Model):
    _inherit = "easy.invoice.line"

    product_uom_qty = fields.Float(string='invoiced amount', related='sale_line_id.product_uom_qty')
    delivered_qty = fields.Float(string='delivered quantity')