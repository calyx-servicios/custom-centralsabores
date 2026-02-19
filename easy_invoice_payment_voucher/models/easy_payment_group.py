from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyPaymentGroup(models.Model):

    _inherit = "easy.payment.group"
    
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('easy.payment.group'))

    @api.multi
    def print_easypayment(self):
        return self.env.ref('easy_invoice_payment_voucher.action_report_easy_paymentgroup').report_action(self)



