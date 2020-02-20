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
        for rec in self:
            if rec.group_type == 'out_group':
                if rec and rec.state == 'draft':#.state != 'processed':
                    amount_total_debt = 0.0
                    amount2pay = 0.0
                    amount_money_defined = rec.amount_money_defined
                    amount_total_rectificative = 0.0
                    
                    invoice_ids = []
                    rectificative_ids = []
                
                    # busco que variables usar
                    if rec.group_type and rec.group_type in ('in_group'):
                        invoice_ids = rec.in_invoice_ids
                        rectificative_ids = rec.in_rectificative_ids
                    if rec.group_type and rec.group_type in ('out_group'):
                        invoice_ids = rec.out_invoice_ids
                        rectificative_ids = rec.out_rectificative_ids

                    # recorro las rectificativas
                    if_invoice_ids,rectificative_ids,amount_total_rectificative = self._control_rectificative_ids(rectificative_ids)

    ## si viene un monto  < 0.00 USAR SOLO LAS NOTAS DE CREDITO Y EL SALGO DEL CLIENTE
    ## si viene un monto == 0.00 usar NOTAS DE CREDITO, MONTO DE CLIENTE y pagar TODO EL RESTO de las facturas
    ## si viene un monto  > 0.00  usar notas de credito, monto de cliente y EL TOTAL DEL MONTO A PAGAR
                    flag_amount_not_defined = True
                    # busco si setea algo de dinero con el cual pagar
                    if amount_money_defined > 0.009:
                        amount_money_defined += self._sum_amount_money_defined(amount_total_rectificative)
                    else:
                        #if amount_money_defined <= 0.009 and amount_money_defined >= -0.009:
                        flag_amount_not_defined = False
                        amount_money_defined = self._sum_amount_money_defined(amount_total_rectificative)
                        #else:
                            #if amount_money_defined < -0.009:
                                #amount_money_defined = self._sum_amount_money_defined(amount_total_rectificative)
    ## hacer que esto calcule bien como quiero y pienso..
                    #recorro las facturas y distribuyo el dinero que va a pagar 
                    for line_obj in invoice_ids:
                        line_obj.residual_amount = line_obj.invoice_id.residual_amount
                        if not str(line_obj.invoice_id.id) in if_invoice_ids:
                            if_invoice_ids[str(line_obj.invoice_id.id)] = line_obj.invoice_id
                        else:
                            raise ValidationError('No se puede agregar 2 veces una Factura (Ref: %s)'%str(line_obj.invoice_id.name))

                        amount_total_debt += line_obj.residual_amount
                        if flag_amount_not_defined:
                            amount2pay += line_obj.amount2pay
                        else:
                            if amount_money_defined >= line_obj.residual_amount:
                                line_obj.amount2pay = line_obj.residual_amount
                                amount2pay += line_obj.amount2pay
                                amount_money_defined -= line_obj.amount2pay
                            else:
                                line_obj.amount2pay = amount_money_defined
                                amount_money_defined = 0.0
                                amount2pay += line_obj.amount2pay
                        line_obj.amount2payed = line_obj.amount2pay
    ## setear correctamente estas variables  la variable amount2pay tiene que terminar en cero para queno cree pagos en la caja

                    rec.amount_money_defined =  amount_money_defined 
                    rec.amount_total_debt = amount_total_debt
                    rec.amount2pay = amount2pay
                    rec.amount_total_rectificative = amount_total_rectificative
                    rec.amount_money = amount2pay - amount_total_rectificative

                if rec.amount_money < 0.0:
                    raise ValidationError(_('You cant not Prepare a Group with Amount Money in 0 or Negative.-'))
                rec._control_amount_partner_cc_ajust()
                rec.amount_difference = rec.amount_total_debt - rec.amount_total_rectificative - rec.partner_amount - rec.partner_amount_anticipe
            else:
                var_return  = super(EasyPaymentGroup, self).control_amount()


    @api.multi
    def prepared2processed(self):
        var_return  = super(EasyPaymentGroup, self).prepared2processed()
        return self.print_easypayment()


    @api.multi
    def _control_amount_partner_cc_ajust(self):
        #aca arreglar el amount_money restando lo de pago el partner anteriormente
        for rec in self:
            if rec.amount_money_defined > 0.0:
                amount2use = rec.amount_money_defined #* (-1.0)
                if amount2use  > 0.009: #rec.partner_cc_id.amount_anticipe:
                    if rec.partner_cc_id and rec.partner_cc_id.amount_anticipe != 0.0:
                        if (rec.partner_cc_id.amount_anticipe*(-1)) > amount2use:
                            rec.partner_amount -= amount2use
                            rec.partner_cc_id.amount_anticipe += amount2use


    @api.multi
    def _sum_amount_money_defined(self,amount_total_rectificative): 
        # in    partner_amount_advancement
        # out   partner_amount_anticipe
        for rec in self:
            var_return = amount_total_rectificative
            if rec.group_type and rec.group_type in ('out_group'):
                rec.partner_amount = rec.partner_amount_anticipe

                if rec.partner_amount != 0.0:
                    amount_total_debt = 0.0
                    for line_obj in rec.out_invoice_ids:
                        amount_total_debt += line_obj.residual_amount

                    if amount_total_debt < rec.partner_amount:
                        rec.partner_amount = amount_total_debt
                    if not rec.partner_cc_id:
                        vals = {
                            'description':'Venta Preparada',
                            'date': rec.date,
                            'partner_id': rec.partner_id.id ,
                            'amount_anticipe' : rec.partner_amount * (-1),
                            'amount_advancement' : 0.0,
                        }
                        rec.partner_cc_id = (self.env['easy.partner.cc'].create(vals)).id
                    else:
                        rec.partner_cc_id.amount_anticipe = rec.partner_amount * (-1)

                return  (var_return + rec.partner_amount)
            else:
                return super(EasyPaymentGroup, self)._sum_amount_money_defined(amount_total_rectificative)

