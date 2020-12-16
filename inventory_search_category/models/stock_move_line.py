# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_category_name = fields.Char(
        string = 'Product Category',
        related = 'product_id.categ_id.name',
    )
    period = fields.Char(
        string = 'Period MM/YY',
        compute = 'compute_period',
        store = True
    )

    @api.depends("period")
    def compute_period(self):
        for rec in self:
            period = fields.Datetime.from_string(rec.date)
            period_month = str(period.month).zfill(2)
            period_year = str(period.year)
            # We calculate the date field with the following format "MM/YY"
            rec.period = period_month + "/" + period_year[-2:]