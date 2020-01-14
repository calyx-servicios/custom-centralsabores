# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"



    # @api.multi
    # @api.depends('pricelist_id')
    # def _compute_pricelist_product_list(self):
    #     for rec in self:
    #         pricelist_product_list_ids =[]
    #         for line_obj in rec.pricelist_id.item_ids:
    #             if line_obj.applied_on == '1_product':  
    #                 self_ids = self.env['product.product'].search([ ('product_tmpl_id', '=', line_obj.product_tmpl_id.id)])
    #                 if self_ids:
    #                     pricelist_product_list_ids.append(self_ids[0].id)
    #         rec.pricelist_product_list_ids = pricelist_product_list_ids


    # @api.model
    # def _get_product_domain(self):
    #     print('             esta viniendo pora ca')
    #     print('             esta viniendo pora ca')
    #     print('             esta viniendo pora ca')
    #     print('             esta viniendo pora ca')
    #     print('             esta viniendo pora ca')
    #     print(self.order_id.pricelist_product_list_ids)
    #     ids = self.order_id.pricelist_product_list_ids.ids
    #     print(ids)
    #     return [('id','in', ids)]

    # product_id = fields.Many2one('product.product', string='Product', change_default=True, ondelete='restrict', required=True,
    #               domain= _get_product_domain  )

    #pricelist_id = fields.Many2one('product.pricelist', string='Pricelist') 
    #pricelist_product_list_ids = fields.Many2many('product.product', 'product_template_pricelist_sale_line_rel', 'product_id', 'pricelist_id', string='List Product')
    
### end Fields
    
    
    