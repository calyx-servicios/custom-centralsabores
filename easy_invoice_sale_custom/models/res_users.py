# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"
      

    default_cost_center_sale_id = fields.Many2one('cost.center', 'Default Cost Center Sale')
    