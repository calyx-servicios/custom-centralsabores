# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
      

    default_product_pricelist_id = fields.Many2one('product.pricelist', 'Default Pricelist Sale')
    