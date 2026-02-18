# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):
        """
        Sobrescribe run_scheduler para bloquear la generación de nuevas PO.
        Ejecuta el scheduler pero bloquea la creación de nuevas PO.
        """
        _logger.info("Purchase Scheduler Block: run_scheduler ejecutado. No se generarán nuevas PO automáticamente.")
        return super(ProcurementGroup, self).run_scheduler(use_new_cursor=use_new_cursor, company_id=company_id)
    