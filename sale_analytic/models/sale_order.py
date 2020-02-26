# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_invoice_line(self, qty):
        res=super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.product_id and self.product_id.product_tmpl_id.analytic_id:
            res['account_analytic_id']= self.product_id.product_tmpl_id.analytic_id.id
        _logger.debug('_prepare_invoice_line %s' , res)
        return res
    
