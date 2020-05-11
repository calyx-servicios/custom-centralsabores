# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

    def _get_report_base_filename(self):
        self.ensure_one()
        return "%s" % (self.name)
