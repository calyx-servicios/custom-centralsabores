# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def unlink(self):
        if self.env.context.get("force_unlink_move_line"):
            ids = tuple(self.ids)
            if not ids:
                return True
            self.env.cr.execute(
                "UPDATE stock_move_line SET picking_id = NULL, move_id = NULL WHERE id IN %s",
                (ids,),
            )
            self.env.cr.execute("SET session_replication_role = 'replica';")
            try:
                self.env.cr.execute("DELETE FROM stock_move_line WHERE id IN %s", (ids,))
            finally:
                self.env.cr.execute("SET session_replication_role = 'origin';")
            return True

        try:
            return super(StockMoveLine, self).unlink()
        except UserError as err:
            message = str(err)
            is_unreserve_error = (
                "It is not possible to unreserve more products" in message
                or "No es posible deshacer la reserva" in message
            )
            if not is_unreserve_error:
                raise

            # Solo forzar si el picking tiene el modo forzado activado.
            if any(not ml.picking_id or not ml.picking_id.force_unlink_enabled for ml in self):
                raise

            return self.with_context(force_unlink_move_line=True).unlink()
