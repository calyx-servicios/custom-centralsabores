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


# ### Fields
#     pricelist_product_list_ids = fields.Many2many('product.product', 'product_template_pricelist_sale_line_rel', 'product_id',
#         'pricelist_id', string='Listo Product',compute='_compute_pricelist_product_list')

# ### end Fields
    
#     @api.multi
#     @api.depends('pricelist_id')
#     def _compute_pricelist_product_list(self):
#         for rec in self:
#             pricelist_product_list_ids =[]
#             for line_obj in rec.pricelist_id.item_ids:
#                 if line_obj.applied_on == '1_product':  
#                     self_ids = self.env['product.product'].search([ ('product_tmpl_id', '=', line_obj.product_tmpl_id.id)])
#                     if self_ids:
#                         pricelist_product_list_ids.append(self_ids[0].id)
#             rec.pricelist_product_list_ids = pricelist_product_list_ids


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        ########
        ## en este metodo deberia de cambiar el precio de lista que se encuentra en el order sale por el que esta configurado por defecto en el partner.
        ########
        if self.partner_id.default_product_pricelist_id:
            self.pricelist_id = self.partner_id.default_product_pricelist_id.id

    @api.onchange('pricelist_id')
    def _onchange_easy_pricelist_id(self):
        for line in self.order_line:
            result = line.product_id_change()
           



    @api.multi
    def create_confirm_invoice_print_report(self):
        #res = self.action_confirm()
        invoice_tuple = self.create_easy_invoice()
        if 'context' in invoice_tuple and 'invoice_obj' in invoice_tuple['context']:
            invoice_tuple['context']['invoice_obj'].confirm()
            
        #self.env['ir.actions.report']._get_report_from_name('easy_invoice.report_easy_invoice').report_action(easy_invoice_obj)

        return self.env['ir.actions.report']._get_report_from_name('easy_invoice.report_easy_invoice').report_action(invoice_tuple['context']['invoice_obj'])


