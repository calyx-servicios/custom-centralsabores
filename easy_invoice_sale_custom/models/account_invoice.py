from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    unit_detail = fields.Float('Pedido Original', digits=(16,2))
    delivered_qty = fields.Float('Delivered Quantity', default = 0, store = True)
    delivery_type = fields.Selection(
        [("additional", "Additional"), ("normal", "Normal"), ("pending", "Pending"), ("birthday_cake", "Birthday cake")],
        string="Delivery type",
        store=True,
    )
    