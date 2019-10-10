# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
      
    @api.multi
    def write(self,vals):
        result =  super(SaleOrder, self).write(vals)
        for line in self.order_line:
            line.product_id_change() 
        return result

    @api.onchange('pricelist_id')
    def _onchange_easy_pricelist_id(self):
        for line in self.order_line:
            result = line.product_id_change()
           

    @api.multi
    def easy_invoice_action_confirm(self):
        res = self.action_confirm()
        invoice_tuple = self.create_easy_invoice()
        if 'context' in invoice_tuple and 'invoice_obj' in invoice_tuple['context']:
            invoice_tuple['context']['invoice_obj'].confirm()
        return res
