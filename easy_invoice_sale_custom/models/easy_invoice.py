# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

    @api.multi
    def rectificate_invoice(self):
        for self_obj in self:

            type_refund = 'in_refund'
            compose_form = self.env.ref(
                'easy_invoice.easy_invoice_supplier_form', False)
            if self_obj.type == 'out_invoice':
                compose_form = self.env.ref(
                    'easy_invoice.easy_invoice_customer_form', False)
                type_refund = 'out_refund'

            vals = {
                'type': type_refund,
                'state': 'draft',
                'partner_id':    self_obj.partner_id.id,
                'company_id': self_obj.company_id.id,
                'rectificative_invoice_id': self_obj.id,
                'date_invoice': fields.Date.today(),
                'date_expiration': fields.Date.today(),
                'configuration_sequence_id': self_obj.configuration_sequence_id.id,

            }
            invoice_created = self.env['easy.invoice'].create(vals)
            self_obj.easy_invoice_id = invoice_created.id
            for line_obj in self_obj.invoice_line_ids:
                vals = {
                    'invoice_id': invoice_created.id,
                    'name': line_obj.name,
                    'price_unit': line_obj.price_unit,
                    'uom_id':    line_obj.uom_id.id,
                    'product_id': line_obj.product_id.id,
                    'quantity': line_obj.quantity,
                    'currency_id': line_obj.currency_id.id,
                    'company_id': line_obj.company_id.id,
                    'unit_detail': line_obj.unit_detail,
                }
                invoice_line_created = self.env[
                    'easy.invoice.line'].create(vals)

            if invoice_created:
                return {
                    'name': _('Rectificative'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'easy.invoice',
                    'res_id': invoice_created.id,
                    'views': [(compose_form.id, 'form')],
                    'view_id': compose_form.id,
                    'context': {},
                }
            return invoice_created


class EasyInvoiceLine(models.Model):
    _inherit = "easy.invoice.line"


    unit_detail = fields.Float('Pedido Original', digits=(16,2))


    # @api.multi
    # def write(self,vals):
    #     invoice_obj =  super(EasyInvoice, self).write(vals)
    #     for line in self.invoice_line_ids:
    #         line._onchange_product_id22()
    #     return invoice_obj
        

    # @api.model
    # def create(self, vals):
    #     invoice_obj = super(EasyInvoice, self).create(vals)
    #     for line in invoice_obj.invoice_line_ids:
    #         line._onchange_product_id22()
    #     return invoice_obj
