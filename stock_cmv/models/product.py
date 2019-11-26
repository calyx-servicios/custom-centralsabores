# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

import logging
_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit = "product.product"

    initial_cost = fields.Float(
        'Initial Cost', compute='_compute_cost', search='_search_cost',
        digits=dp.get_precision('Product Unit of Measure'),
        help="")
    cost = fields.Float(
        'Period Cost', compute='_compute_cost', search='_search_cost',
        digits=dp.get_precision('Product Unit of Measure'),
        help="")
    final_cost = fields.Float(
        'Final Cost', compute='_compute_cost', search='_search_cost',
        digits=dp.get_precision('Product Unit of Measure'),
        help="")


    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_cost(self):
        res = self._compute_cost_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in self:
            product.initial_cost = res[product.id]['initial_cost']
            product.cost = res[product.id]['cost']
            product.final_cost = res[product.id]['final_cost']

    def _compute_cost_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        if from_date and from_date < fields.Datetime.now(): #Only to_date as to_date will correspond to qty_available
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        intial_domain_in =[]
        intial_domain_out =[]
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
            intial_domain_in = domain_move_in_done
            intial_domain_out = domain_move_out_done
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
            
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_done = [('state', 'in', ('done',))] + domain_move_in
        domain_move_out_done= [('state', 'in', ('done',))] + domain_move_out
        moves_in_res={}
        moves_out_res={}
        moves_in_initial={}
        moves_out_initial={}
       
        _logger.debug('>>>>=====moves_in_done filter:%r=====<<<<',domain_move_in_done)
        for move in Move.search(domain_move_in_done):
            _logger.debug('=====moves_in_donde=====%r %r %r %r', move.product_id.name, move.price_unit, move.product_qty, move.origin)
            if not move.product_id.name in moves_in_res:
                moves_in_res.setdefault(move.product_id.id, {'count':0, 'avg':0.0})
            if move.purchase_line_id:
                _logger.debug('=====purchase_line=====%r %r', move.purchase_line_id.order_id.name, move.purchase_line_id.price_unit)
                moves_in_res[move.product_id.id]['count']+=move.product_uom_qty
                moves_in_res[move.product_id.id]['avg']+= move.purchase_line_id.price_unit*move.product_uom_qty
            else:
                moves_in_res[move.product_id.id]['count']+=move.product_uom_qty
                moves_in_res[move.product_id.id]['avg']+= move.price_unit*move.product_uom_qty
            
        _logger.debug('>>>>=====moves_out_done filter:%r=====<<<<',domain_move_out_done) 
        for move in Move.search(domain_move_out_done):
            _logger.debug('=====moves_out_done=====%r %r %r', move.product_id.name, move.price_unit, move.product_qty)
            if not move.product_id.name in moves_out_res:
                moves_out_res.setdefault(move.product_id.id, {'count':0, 'avg':0.0})
            if move.sale_line_id:
                _logger.debug('=====sale_line=====%r %r', move.sale_line_id.order_id.name, move.sale_line_id.price_unit)
                moves_out_res[move.product_id.id]['count']+=move.product_uom_qty
                moves_out_res[move.product_id.id]['avg']+= move.sale_line_id.price_unit*move.product_uom_qty
            else:
                moves_out_res[move.product_id.id]['count']+=move.product_uom_qty
                moves_out_res[move.product_id.id]['avg']+= move.price_unit*move.product_uom_qty
           
                
        # moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        # moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
        _logger.debug('=====moves_in_res=====%r', moves_in_res)
        _logger.debug('=====moves_out_res=====%r', moves_out_res)
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            _logger.debug('>>>>=====moves_in_done dates_in_the_past=====<<<<')
            domain_move_in_done = [('state', '=', 'done'),('date', '<', from_date)] + intial_domain_in
            domain_move_out_done = [('state', '=', 'done'), ('date', '<', from_date)] + intial_domain_out
            _logger.debug('>>>>=====moves_in_done_past filter:%r=====<<<<',domain_move_in_done)
            _logger.debug('>>>>=====moves_out_done_past filter:%r=====<<<<',domain_move_out_done)
            for move in Move.search(domain_move_in_done):
                if not move.product_id.name in moves_in_initial:
                    moves_in_initial.setdefault(move.product_id.id, {'count':0, 'avg':0.0})
                if move.purchase_line_id:
                    _logger.debug('=====purchase_line=====%r %r', move.purchase_line_id.order_id.name, move.purchase_line_id.price_unit)
                    moves_in_initial[move.product_id.id]['count']+=move.product_uom_qty
                    moves_in_initial[move.product_id.id]['avg']+= move.purchase_line_id.price_unit*move.product_uom_qty
                else:
                    moves_in_initial[move.product_id.id]['count']+=move.product_uom_qty
                    moves_in_initial[move.product_id.id]['avg']+= move.price_unit*move.product_uom_qty
            for move in Move.search(domain_move_out_done):
                if not move.product_id.name in moves_out_initial:
                    moves_out_initial.setdefault(move.product_id.id, {'count':0, 'avg':0.0})
                if move.sale_line_id:
                    _logger.debug('=====sale_line=====%r %r', move.sale_line_id.order_id.name, move.sale_line_id.price_unit)
                    moves_out_initial[move.product_id.id]['count']+=move.product_uom_qty
                    moves_out_initial[move.product_id.id]['avg']+= move.sale_line_id.price_unit*move.product_uom_qty
                else:
                    moves_out_initial[move.product_id.id]['count']+=move.product_uom_qty
                    moves_out_initial[move.product_id.id]['avg']+= move.price_unit*move.product_uom_qty

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            _logger.debug('=====product=====%r', product.name)
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            initial_cost=0.0
            cost=0.0
            final_cost=0.0
            initial_in_cost=0.0
            initial_out_cost=0.0
            period_in_cost=0.0
            period_out_cost=0.0
            if moves_in_initial.get(product_id):
                initial_in_cost=moves_in_initial.get(product_id)['avg']/moves_in_initial.get(product_id)['count']
            if moves_out_initial.get(product_id):
                initial_out_cost=moves_out_initial.get(product_id)['avg']/moves_out_initial.get(product_id)['count']
            initial_cost=initial_in_cost-initial_out_cost

            if moves_in_res.get(product_id):
                period_in_cost=moves_in_res.get(product_id)['avg']/moves_in_res.get(product_id)['count']
            if moves_out_res.get(product_id):
                period_out_cost=moves_out_res.get(product_id)['avg']/moves_out_res.get(product_id)['count']
            cost=period_in_cost-period_out_cost
            final_cost=initial_cost+cost
            res[product_id]['initial_cost'] = float_round(initial_cost, precision_rounding=rounding)
            res[product_id]['cost'] = float_round(cost, precision_rounding=rounding)
            res[product_id]['final_cost'] = float_round(final_cost, precision_rounding=rounding)

        return res
    
    def _search_cost(self, operator, value):
        # In the very specific case we want to retrieve products with stock available, we only need
        # to use the quants, not the stock moves. Therefore, we bypass the usual
        # '_search_product_quantity' method and call '_search_qty_available_new' instead. This
        # allows better performances.
        if value == 0.0 and operator == '>' and not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
            return [('id', 'in', product_ids)]
        return self._search_product_quantity(operator, value, 'qty_available')