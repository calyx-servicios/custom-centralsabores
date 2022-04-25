from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_type = fields.Selection(
        [("additional", "Additional"), ("normal", "Normal"), ("pending", "Pending")],
        string="Delivery type",
        store=True,
    )

    @api.multi
    def action_confirm(self):
        if not self.delivery_type:
            raise ValidationError(_("Delivery type is required"))
        else:
            super(SaleOrder, self).action_confirm()

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        for line in self.order_line:
            line.product_id_change()
        return result

    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     ########
    #     ## en este metodo deberia de cambiar el precio de lista que se encuentra en el order sale por el que esta configurado por defecto en el partner.
    #     ########
    #     if self.partner_id.default_product_pricelist_id:
    #         self.pricelist_id = self.partner_id.default_product_pricelist_id.id

    @api.onchange('pricelist_id')
    def _onchange_easy_pricelist_id(self):
        for line in self.order_line:
            result = line.product_id_change()

    @api.multi
    def create_confirm_invoice_print_report(self):
        invoice_tuple = self.create_easy_invoice()
        if 'context' in invoice_tuple and 'invoice_obj' in invoice_tuple['context']:
            invoice_tuple['context']['invoice_obj'].confirm()
        return self.env['ir.actions.report']._get_report_from_name('easy_invoice.report_easy_invoice').report_action(invoice_tuple['context']['invoice_obj'])


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    unit_detail = fields.Float('Pedido Original', digits=(16,2))
    
    delivered_qty = fields.Float('Delivered Quantity', default = 0, store = True)
    delivery_type = fields.Selection(related='order_id.delivery_type', store=True)
    def _prepare_line_easy_invoice(self, invoice_created):
        """We add the unit_detail field to the dictionary of values ​​
           so that it loads it in the easy invoice """
        res = super(SaleOrderLine, self)._prepare_line_easy_invoice(invoice_created)
        res['unit_detail'] = self.unit_detail
        res['delivered_qty'] = self.delivered_qty
        res['delivery_type'] = self.delivery_type
        return res