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

    @api.model
    def _default_cost_center(self):
        return None
        if self.env.user.default_cost_center_sale_id:
            return self.env.user.default_cost_center_sale_id.id
        return None

### Fields
    cost_center_id = fields.Many2one('cost.center', 'Cost Center',default=_default_cost_center)
### end Fields

    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        print('antes del otro')
        #result =  super(SaleOrder, self)._onchange_partner_id() 
        print('entra al onchange')
        print(self.partner_id.default_product_pricelist_id)
        print('entra al onchange')
        if self.partner_id.default_product_pricelist_id:
            self.pricelist_id = self.partner_id.default_product_pricelist_id.id
            print('setea el valor')
        #return result


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
