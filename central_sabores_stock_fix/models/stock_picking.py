# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_suppress_moves_force(self):
        reusable_delete_model = self.env["reusable.sql.delete"].sudo()
        deleted_move_ids = []
        failed_picking_ids = []

        for picking in self:
            if picking.state not in ("waiting", "assigned"):
                failed_picking_ids.append(picking.id)
                continue

            move_ids = picking.move_lines.ids
            if not move_ids:
                continue

            try:
                reusable_delete_model.delete_records("stock.move", "picking_id", picking.id)
            except UserError as err:
                message = str(err)
                if "Se eliminaron los siguientes IDs" in message:
                    deleted_move_ids.extend(move_ids)
                elif "No se encontraron registros" in message:
                    continue
                else:
                    failed_picking_ids.append(picking.id)
            except Exception:
                failed_picking_ids.append(picking.id)

        if failed_picking_ids:
            raise UserError(
                _("No se pudo suprimir moves. Modelo: stock.picking, ID: %s")
                % ", ".join(map(str, failed_picking_ids))
            )

        if deleted_move_ids:
            raise UserError(
                _("Registros suprimidos. Modelo: stock.move, ID: %s")
                % ", ".join(map(str, deleted_move_ids))
            )

        raise UserError(_("No se encontraron moves para suprimir."))

    @api.multi
    def action_suppress_force(self):
        reusable_delete_model = self.env["reusable.sql.delete"].sudo()
        deleted_picking_ids = []
        failed_ids = []

        for picking in self:
            if picking.state not in ("waiting", "assigned"):
                failed_ids.append(picking.id)
                continue

            try:
                reusable_delete_model.delete_records("stock.picking", "id", picking.id)
            except UserError as err:
                # El modulo reutilizable usa UserError tambien para informar exito.
                if "Se eliminaron los siguientes IDs" in str(err):
                    deleted_picking_ids.append(picking.id)
                else:
                    failed_ids.append(picking.id)
            except Exception:
                failed_ids.append(picking.id)

        if failed_ids:
            raise UserError(
                _("No se pudo suprimir. Modelo: stock.picking, ID: %s")
                % ", ".join(map(str, failed_ids))
            )

        if deleted_picking_ids:
            raise UserError(
                _("Registros suprimidos. Modelo: stock.picking, ID: %s")
                % ", ".join(map(str, deleted_picking_ids))
            )

        return True
