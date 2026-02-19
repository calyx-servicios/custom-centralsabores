# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_scheduler_block_days_limit = fields.Integer(
        string='Días límite para validación de PO',
        default=2,
        help='Número de días hacia atrás desde la fecha actual para validar '
             'órdenes de compra pendientes. Solo se validarán PO creadas después '
             'de esta fecha límite (hora 00:00:00).'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            purchase_scheduler_block_days_limit=int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'purchase_scheduler_block.days_limit', '2'
                )
            )
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'purchase_scheduler_block.days_limit',
            str(self.purchase_scheduler_block_days_limit)
        )

