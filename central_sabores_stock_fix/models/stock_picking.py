# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo import fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"
    force_unlink_enabled = fields.Boolean(
        string="Forzado de lineas activo",
        default=False,
        copy=False,
    )

    @api.multi
    def action_enable_force_unlink(self):
        self.write({"force_unlink_enabled": True})
        return {"type": "ir.actions.client", "tag": "reload"}

    @api.multi
    def action_disable_force_unlink(self):
        self.write({"force_unlink_enabled": False})
        return {"type": "ir.actions.client", "tag": "reload"}

    @api.multi
    def action_suppress_force(self):
        deleted_ids = []
        failed_ids = []

        for picking in self:
            if picking.state not in ("waiting", "assigned"):
                failed_ids.append(picking.id)
                continue

            try:
                # Suprimir completo: lineas, moves y picking.
                self.env.cr.execute(
                    "UPDATE stock_move_line SET picking_id = NULL, move_id = NULL WHERE picking_id = %s",
                    (picking.id,),
                )
                self.env.cr.execute("SET session_replication_role = 'replica';")
                try:
                    self.env.cr.execute("DELETE FROM stock_move_line WHERE picking_id = %s", (picking.id,))
                    self.env.cr.execute("DELETE FROM stock_move WHERE picking_id = %s", (picking.id,))
                    self.env.cr.execute("DELETE FROM stock_picking WHERE id = %s", (picking.id,))
                finally:
                    self.env.cr.execute("SET session_replication_role = 'origin';")
                deleted_ids.append(picking.id)
            except Exception:
                failed_ids.append(picking.id)

        if failed_ids:
            raise UserError(
                _("No se pudo suprimir. Modelo: stock.picking, ID: %s")
                % ", ".join(map(str, failed_ids))
            )

        if deleted_ids:
            return {"type": "ir.actions.client", "tag": "reload"}

        return {"type": "ir.actions.client", "tag": "reload"}
