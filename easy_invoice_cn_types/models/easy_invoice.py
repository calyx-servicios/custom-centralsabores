from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

    cn_types_id = fields.Many2one(
        comodel_name="easy.invoice.cn.types", string="CN Types",
    )