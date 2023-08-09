from odoo import fields, models
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        #que no se puedan ingresar 2 veces la misma lista de precios en el producto
        if 'item_ids' in vals:
            for pricelist in vals['item_ids']:
                if pricelist[0] == 0:
                    for current_pricelist in self.item_ids:
                        if current_pricelist.pricelist_id.id == pricelist[2]['pricelist_id']:
                            raise UserError(('No puede ingresar la misma lista de precios mas de una vez.'))
                    for new_pricelist in vals['item_ids']:
                        if new_pricelist[0] == 0:
                            if new_pricelist[1] != pricelist[1] and new_pricelist[2]['pricelist_id'] == pricelist[2]['pricelist_id']:
                                raise UserError(('No puede ingresar la misma lista de precios mas de una vez.'))

        super(ProductTemplate, self).write(vals)

    def chek_pricelist_duplicated(self):

        return False
