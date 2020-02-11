# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoiceLine(models.Model):
    
    _inherit = "easy.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id22(self):
        for rec in self:
            if rec.invoice_id.type in ('out_invoice','out_refund') and rec.invoice_id.partner_id.default_product_pricelist_id:
                for line_obj in rec.invoice_id.partner_id.default_product_pricelist_id.item_ids:
                    if line_obj.applied_on == '1_product':
                        self_ids = rec.env['product.product'].search([ ('product_tmpl_id', '=', line_obj.product_tmpl_id.id)])
                        if self_ids:
                            if self_ids[0].id == rec.product_id.id:
                                rec.price_unit = line_obj.fixed_price