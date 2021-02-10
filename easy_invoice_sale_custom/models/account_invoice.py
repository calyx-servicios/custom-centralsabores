from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    unit_detail = fields.Float('Detalle Unidad', digits=(16,2))

    