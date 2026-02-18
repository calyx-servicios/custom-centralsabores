# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, values):
        """
        Valida que no se puedan crear/modificar PO con productos que ya tienen
        órdenes de compra pendientes de pago o en borrador.
        """
        # Si se están agregando o modificando líneas de pedido, validar productos
        if 'order_line' in values:
            # Obtener productos de las líneas que se están agregando o modificando
            product_ids = []
            for line_command in values['order_line']:
                if isinstance(line_command, (list, tuple)) and len(line_command) >= 3:
                    command = line_command[0]
                    if command == 0:  # create - nueva línea
                        line_vals = line_command[2] if len(line_command) > 2 else {}
                        if 'product_id' in line_vals:
                            product_ids.append(line_vals['product_id'])
                    elif command == 1:  # update - línea existente
                        line_vals = line_command[2] if len(line_command) > 2 else {}
                        if 'product_id' in line_vals:
                            product_ids.append(line_vals['product_id'])
                    # command == 2 es delete, no necesitamos validar
                    # command == 3 es link, no necesitamos validar
                    # command == 4 es unlink, no necesitamos validar
                    # command == 5 es clear, no necesitamos validar
                    # command == 6 es replace, no lo usamos aquí
            
            # Si hay productos, validar que no tengan PO pendientes
            # Excluir las PO actuales de la validación
            if product_ids:
                self._check_products_pending_po(product_ids, exclude_po_ids=self.ids)
        
        return super(PurchaseOrder, self).write(values)

    @api.model
    def create(self, values):
        """
        Valida que no se puedan crear PO con productos que ya tienen
        órdenes de compra pendientes de pago o en borrador.
        """
        # Obtener productos de las líneas que se están creando
        product_ids = []
        if 'order_line' in values:
            for line_command in values['order_line']:
                if isinstance(line_command, (list, tuple)) and len(line_command) >= 3:
                    command = line_command[0]
                    if command == 0:  # create
                        line_vals = line_command[2] if len(line_command) > 2 else {}
                        if 'product_id' in line_vals:
                            product_ids.append(line_vals['product_id'])
        
        # Si hay productos, validar que no tengan PO pendientes
        if product_ids:
            self._check_products_pending_po(product_ids)
        
        return super(PurchaseOrder, self).create(values)

    def _get_date_limit(self):
        """
        Calcula la fecha límite para validar PO.
        Retorna la fecha actual menos los días configurados, con hora 00:00:00.
        
        :return: datetime con la fecha límite (hora 00:00:00)
        """
        # Obtener días del parámetro de sistema (por defecto 2)
        days_limit = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'purchase_scheduler_block.days_limit', '2'
            )
        )
        
        # Calcular fecha límite: fecha actual - días configurados
        date_limit = datetime.now() - timedelta(days=days_limit)
        
        # Poner la hora a 00:00:00
        date_limit = date_limit.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return date_limit

    def _check_products_pending_po(self, product_ids, exclude_po_ids=None):
        """
        Verifica si los productos tienen órdenes de compra pendientes.
        Estados a verificar: 'draft', 'sent', 'to approve', 'purchase' (si no están pagadas)
        Solo valida PO creadas después de la fecha límite configurada.
        
        :param product_ids: Lista de IDs de productos a verificar
        :param exclude_po_ids: Lista de IDs de PO a excluir de la validación (PO actual)
        """
        if not product_ids:
            return
        
        exclude_po_ids = exclude_po_ids or []
        
        # Obtener fecha límite
        date_limit = self._get_date_limit()
        date_limit_str = date_limit.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        # Buscar líneas de PO con estos productos en estados pendientes
        pending_states = ['draft', 'sent', 'to approve', 'purchase']
        
        # Buscar PO en estados pendientes con estos productos, excluyendo las PO actuales
        # y solo las creadas después de la fecha límite
        domain = [
            ('product_id', 'in', product_ids),
            ('order_id.state', 'in', pending_states),
            ('order_id.create_date', '>=', date_limit_str),
        ]
        if exclude_po_ids:
            domain.append(('order_id.id', 'not in', exclude_po_ids))
        
        pending_po_lines = self.env['purchase.order.line'].search(domain)
        
        if pending_po_lines:
            # Filtrar las que no están pagadas completamente (si tienen estado 'purchase')
            # Para PO en estado 'purchase', verificar si están pagadas
            purchase_po_lines = pending_po_lines.filtered(
                lambda l: l.order_id.state == 'purchase'
            )
            
            # Verificar si las PO en estado 'purchase' están pagadas
            # Usar advance_payment_status si existe, sino usar invoice_status
            unpaid_purchase_lines = purchase_po_lines.filtered(
                lambda l: self._is_po_unpaid(l.order_id)
            )
            
            # Combinar líneas pendientes (draft, sent, to approve) con las no pagadas
            other_pending_lines = pending_po_lines.filtered(
                lambda l: l.order_id.state in ['draft', 'sent', 'to approve']
            )
            
            all_pending_lines = other_pending_lines | unpaid_purchase_lines
            
            if all_pending_lines:
                # Agrupar por producto
                products_with_po = {}
                for line in all_pending_lines:
                    product = line.product_id
                    if product.id not in products_with_po:
                        products_with_po[product.id] = {
                            'product': product,
                            'po_names': []
                        }
                    po_name = line.order_id.name or _('Sin número')
                    if po_name not in products_with_po[product.id]['po_names']:
                        products_with_po[product.id]['po_names'].append(po_name)
                
                # Construir mensaje de error
                product_messages = []
                for product_data in products_with_po.values():
                    po_list = ', '.join(product_data['po_names'])
                    product_messages.append(
                        _("- %s (PO: %s)") % (product_data['product'].display_name, po_list)
                    )
                
                error_message = _(
                    "No se puede crear/modificar la orden de compra porque ya existen "
                    "órdenes de compra pendientes o sin pagar para los siguientes productos:\n\n%s"
                ) % '\n'.join(product_messages)
                
                raise UserError(error_message)
    
    def _is_po_unpaid(self, po):
        """
        Verifica si una PO está sin pagar o parcialmente pagada.
        
        :param po: purchase.order record
        :return: True si la PO no está completamente pagada
        """
        # Si tiene advance_payment_status, usar ese campo
        if hasattr(po, 'advance_payment_status'):
            return po.advance_payment_status in ['not_paid', 'partial']
        
        # Si no, verificar por invoice_status
        # Si está 'invoiced' completamente, considerar pagada
        # Si está 'to invoice' o 'no', considerar no pagada
        if po.invoice_status == 'invoiced':
            return False
        
        return True

