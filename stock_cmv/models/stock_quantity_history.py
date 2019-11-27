# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import datetime

from odoo import api, fields, models, _


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'
    compute_at_date = fields.Selection([
        (0, 'Current Inventory'),
        (1, 'At a Specific Date'),
        (2, 'Range Date')
    ], string="Compute", help="Choose to analyze the current inventory or from a specific date in the past.")
    compute_method = fields.Selection([
        (0, 'Default'),
        (1, 'CMV')
    ], string="Calculation Method", help="", default=0)

    @api.model
    def _get_from_date(self):
        _from_date=datetime.datetime.now()# - datetime.timedelta(days=3*365)
        return _from_date

    from_date = fields.Datetime('Inventory From Date', default=_get_from_date)
    

    def open_table(self):
        self.ensure_one()

        if self.compute_method==0:
            return super(StockQuantityHistory, self).open_table()
        else:
            if self.compute_at_date:
                tree_view_id = self.env.ref('stock_cmv.view_stock_product_tree_custom').id
                form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
                # We pass `to_date` in the context so that `qty_available` will be computed across
                # moves until date.
                action = {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'name': _('Products'),
                    'res_model': 'product.product',
                    'domain': "[('type', '=', 'product'), ('qty_available', '!=', 0)]",
                    'context': dict(self.env.context, to_date=self.date,from_date=self.from_date),
                }
                return action
            else:
                self.env['stock.quant']._merge_quants()
                return self.env.ref('stock.quantsact').read()[0]
    
    
           
