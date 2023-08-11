from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        if 'item_ids' in vals:
            for pricelist in vals['item_ids']:
                for other_pricelist in vals['item_ids']:
                    if other_pricelist[1] != pricelist[1] and other_pricelist[2]['pricelist_id'] == pricelist[2]['pricelist_id']:
                        raise UserError(('You cannot enter the same price list more than once.'))

        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        #You cannot enter the same price list more than once.
        if 'item_ids' in vals:
            for pricelist in vals['item_ids']:
                if pricelist[0] == 0:
                    for current_pricelist in self.item_ids:
                        if current_pricelist.pricelist_id.id == pricelist[2]['pricelist_id']:
                            raise UserError(('You cannot enter the same price list more than once.'))
                    for new_pricelist in vals['item_ids']:
                        if new_pricelist[0] == 0:
                            if new_pricelist[1] != pricelist[1] and new_pricelist[2]['pricelist_id'] == pricelist[2]['pricelist_id']:
                                raise UserError(('You cannot enter the same price list more than once.'))

        super(ProductTemplate, self).write(vals)
