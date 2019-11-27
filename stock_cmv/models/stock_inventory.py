# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils

import logging
_logger = logging.getLogger(__name__)




class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    
    product_price = fields.Float('Price',)


class Inventory(models.Model):
    _inherit = "stock.inventory"

    def action_done(self):
        data=super(Inventory, self).action_done()
        prices={}
        for line in self.line_ids:
            if not line.product_id.id in prices:
                prices.setdefault(line.product_id.id, line.product_price)
            else:
                if prices[line.product_id.id]<line.product_price:
                    prices[line.product_id.id]=line.product_price
        for move in self.move_ids:
            _logger.debug('========Force Move Price for Product:%r  %r=> $$$:%r==========',move.product_id.name, move.price_unit,prices[move.product_id.id])
            move.price_unit=prices[move.product_id.id]
        return data
 
    
    

    
           
