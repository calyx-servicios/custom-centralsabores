# -*- coding: utf-8 -*-

from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_category_name = fields.Char(
        string = 'Product Category',
        related = 'product_tmpl_id.categ_id.name',
    )