# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"


    @api.multi
    def write(self,vals):
        invoice_obj =  super(EasyInvoice, self).write(vals)
        for line in self.invoice_line_ids:
            line._onchange_product_id2()
        return invoice_obj
        

    @api.model
    def create(self, vals):
        invoice_obj = super(EasyInvoice, self).create(vals)
        for line in invoice_obj.invoice_line_ids:
            line._onchange_product_id2()
        return invoice_obj

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist') 

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        ########
        ## en este metodo deberia de cambiar el precio de lista que se encuentra en el order sale por el que esta configurado por defecto en el partner.
        ########
        if self.partner_id.default_product_pricelist_id:
            self.pricelist_id = self.partner_id.default_product_pricelist_id.id
