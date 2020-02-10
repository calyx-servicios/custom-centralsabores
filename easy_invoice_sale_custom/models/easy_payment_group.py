# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


## esto no se esta usando pr que tengo un problema con el escenario

class EasyPaymentGroup(models.Model):
    _inherit = "easy.payment.group"

    amount_difference = fields.Monetary(string='Amount Diference', ) #compute='control_amount', 


    @api.multi
    def control_amount(self):
        var_return  = super(EasyPaymentGroup, self).control_amount()
        for rec in self:
            rec.amount_difference = rec.amount_total_debt - rec.amount_total_rectificative - rec.partner_amount_anticipe - rec.partner_amount
        return var_return




    @api.multi
    def prepared2processed(self):
        var_return  = super(EasyPaymentGroup, self).prepared2processed()
        return self.print_easypayment()

