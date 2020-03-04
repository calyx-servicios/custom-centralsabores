# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"


    # @api.multi
    # def write(self,vals):
    #     invoice_obj =  super(EasyInvoice, self).write(vals)
    #     for line in self.invoice_line_ids:
    #         line._onchange_product_id22()
    #     return invoice_obj
        

    # @api.model
    # def create(self, vals):
    #     invoice_obj = super(EasyInvoice, self).create(vals)
    #     for line in invoice_obj.invoice_line_ids:
    #         line._onchange_product_id22()
    #     return invoice_obj
