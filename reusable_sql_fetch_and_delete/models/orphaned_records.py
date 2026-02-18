# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ReusableSqlDelete(models.Model):
    _name = 'reusable.sql.delete'
    _description = 'Reusable SQL Delete'

    @api.model
    def action_show_popup(self):
        """Acción de ejemplo para mostrar un popup."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Popup Message',
            'res_model': 'ir.cron',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_name': 'This is a message!',
            },
        }

    @api.model
    def get_records(self, model_name, field_name, field_value):
        """
        Obtener registros de una tabla basándose en el valor de un campo.
        
        :param model_name: Nombre del modelo (ej: 'account.move.line' o 'stock.picking')
        :param field_name: Nombre del campo a buscar
        :param field_value: Valor del campo a buscar
        :return: Lista de tuplas con los IDs encontrados
        """
        # Convertir el nombre del modelo a nombre de tabla
        table_name = model_name.replace('.', '_')
        
        # Validar que el modelo existe
        try:
            # Intentar acceder al modelo directamente
            model_obj = self.env[model_name]
            
            # Validar que el campo existe en el modelo
            if field_name not in model_obj._fields:
                raise UserError(_("El campo '%s' no existe en el modelo '%s'.") % (field_name, model_name))
        except KeyError:
            # Si el modelo no está en el registry, verificar si la tabla existe directamente
            # Esto puede pasar con modelos que no están cargados o tablas directas
            self.env.cr.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table_name,))
            table_exists = self.env.cr.fetchone()[0]
            if not table_exists:
                raise UserError(_("El modelo '%s' no existe y la tabla '%s' tampoco existe en la base de datos.") % (model_name, table_name))
            # Si la tabla existe pero el modelo no, continuar de todas formas
            # (puede ser una tabla directa sin modelo Odoo)
        except Exception as e:
            # Si hay otro error, verificar la tabla directamente
            try:
                self.env.cr.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, (table_name,))
                table_exists = self.env.cr.fetchone()[0]
                if not table_exists:
                    raise UserError(_("Error al acceder al modelo '%s': %s") % (model_name, str(e)))
            except:
                raise UserError(_("Error al acceder al modelo '%s': %s") % (model_name, str(e)))
        
        # Ejecutar la consulta
        query = """
            SELECT id 
            FROM %s 
            WHERE %s = %%s
        """ % (table_name, field_name)
        
        self.env.cr.execute(query, (field_value,))
        return self.env.cr.fetchall()

    @api.model
    def create_notification(self):
        """Crear una notificación (para Odoo 11, usar wizard en lugar de notificación cliente)."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Warning!'),
                'message': 'My message',
                'sticky': False,
            }
        }

    @api.model
    def get_record_ids(self, model_name, field_name, field_value):
        """
        Obtener los IDs de los registros en una tabla donde el campo especificado coincide con el valor.
        
        :param model_name: Nombre del modelo (ej: 'account.move.line')
        :param field_name: Nombre del campo a buscar
        :param field_value: Valor del campo a buscar
        :return: Lista de IDs encontrados
        """
        result = self.get_records(model_name, field_name, field_value)
        ids = [record[0] for record in result]
        
        if ids:
            ids_str = ", ".join(map(str, ids))
            _logger.info(
                "Se encontraron los siguientes IDs: %s para el modelo '%s' y el campo '%s' con valor '%s'.",
                ids_str, model_name, field_name, field_value
            )
            raise UserError(
                _("Se encontraron los siguientes IDs: %s para el modelo '%s' y el campo '%s' con valor '%s'.")
                % (ids_str, model_name, field_name, field_value)
            )
        else:
            _logger.info(
                "No se encontraron registros con %s = %s en %s.",
                field_name, field_value, model_name
            )
            raise UserError(
                _("No se encontraron registros con %s = %s en %s.")
                % (field_name, field_value, model_name)
            )

    @api.model
    def delete_records(self, model_name, field_name, field_value):
        """
        Eliminar registros basados en el valor de un campo.
        
        :param model_name: Nombre del modelo (ej: 'account.move.line')
        :param field_name: Nombre del campo a buscar
        :param field_value: Valor del campo a buscar
        :return: True si se eliminaron registros, False si no se encontraron
        """
        result = self.get_records(model_name, field_name, field_value)
        ids = [record[0] for record in result]
        
        if not ids:
            _logger.info(
                "No se encontraron registros con %s = %s en %s para eliminar.",
                field_name, field_value, model_name
            )
            raise UserError(
                _("No se encontraron registros con %s = %s en %s.")
                % (field_name, field_value, model_name)
            )
        
        try:
            # Convertir el nombre del modelo a nombre de tabla
            table_name = model_name.replace('.', '_')
            
            # Desactivar restricciones de foreign key temporalmente
            self.env.cr.execute("SET session_replication_role = 'replica';")
            
            # Ejecutar la eliminación
            query = "DELETE FROM %s WHERE id IN %%s" % table_name
            self.env.cr.execute(query, (tuple(ids),))
            
            # Restaurar restricciones
            self.env.cr.execute("SET session_replication_role = 'origin';")
            
            # Commit de la transacción
            self.env.cr.commit()
            
            ids_str = ", ".join(map(str, ids))
            _logger.info(
                "Se eliminaron los siguientes IDs: %s para el modelo '%s' y el campo '%s' con valor '%s'.",
                ids_str, model_name, field_name, field_value
            )
            
            # Lanzar mensaje informativo
            raise UserError(
                _("Se eliminaron los siguientes IDs: %s para el modelo '%s' y el campo '%s' con valor '%s'.")
                % (ids_str, model_name, field_name, field_value)
            )
            
        except Exception as e:
            # Si hubo un error, hacer rollback
            self.env.cr.rollback()
            # Restaurar restricciones en caso de error
            try:
                self.env.cr.execute("SET session_replication_role = 'origin';")
            except:
                pass
            
            _logger.error("Error al eliminar los registros: %s", str(e))
            raise UserError(_("Error al eliminar los registros: %s") % str(e))

# Ejemplos de uso:                
#model.get_record_ids('account_move_line', 'move_id', 6119)
#model.delete_records('account_move_line', 'move_id', 6119)