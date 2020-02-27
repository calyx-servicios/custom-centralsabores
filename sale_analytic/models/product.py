# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')