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
        print(self.env.user.partner_id)
        if self.env.user.partner_id.default_cost_center_sale_id:
            return self.env.user.partner_id.default_cost_center_sale_id.id
        return None

### Fields
    cost_center_id = fields.Many2one('cost.center', 'Cost Center',default=_default_cost_center)
    #pricelist_product_list_ids = fields.Many2many('product.template', 'product_template_pricelist_sale_rel', 'product_id', 'pricelist_id', string='Listo Product',compute='_compute_pricelist_product_list')
    
### end Fields
    
    @api.multi
    @api.depends('pricelist_id')
    def _compute_pricelist_product_list(self):
        for rec in self:
            pricelist_product_list_ids =[]
            for line_obj in rec.pricelist_id.item_ids:
                if line_obj.applied_on == '1_product':  
                    pricelist_product_list_ids.append(line_obj.product_tmpl_id.id)
            rec.pricelist_product_list_ids = pricelist_product_list_ids


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        ########
        ## en este metodo deberia de cambiar el precio de lista que se encuentra en el order sale por el que esta configurado por defecto en el partner.
        ########
        if self.partner_id.default_product_pricelist_id:
            self.pricelist_id = self.partner_id.default_product_pricelist_id.id
            print('   setea el valor def ')

    @api.onchange('pricelist_id')
    def _onchange_easy_pricelist_id(self):
        for line in self.order_line:
            result = line.product_id_change()
           
