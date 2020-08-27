# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class stockGoldMove(models.TransientModel):
    _name = 'stock.move.gold'
    _description = 'Generate move for all selected moves'

    move_ids = fields.Many2many('stock.valuation.layer', 'move_line_stock_valuation_rel', 'stock_gold_id', 'stock_valuation_id',  'moves', readonly=False)
    pure_weight = fields.Float('pure weight')
    pure_remainning = fields.Float('pure remainning',compute="get_pure_weight_remain")

    @api.depends('move_ids')
    def get_pure_weight_remain(self):
        pure = 0.00
        for rec in self.move_ids:
            pure = pure + rec.paid_pure
        self.pure_remainning = self.pure_weight 

    def compute_sheet(self):
        [data] = self.read()
        if not data['move_ids']:
            raise UserError(_("You must select move(s) to generate payment(s)."))

        active_id = self.env.context.get('active_id')

        if active_id:
            account_move = self.env['account.move'].search([('id' ,'=', active_id)])
            purchase_order = self.env['purchase.order'].search([('name','=' ,account_move.invoice_origin)])

        pure = 0.00
        gross_weight = 0.00
        purity = 0.00
        for move in self.env['stock.valuation.layer'].browse(data['move_ids']):
            pure = pure + move.paid_pure
            gross_weight = gross_weight + move.paid_gross
            purity = purity + move.purity
            product_id = move.product_id
            if  move.paid_gross > move.gross_weight :
                raise UserError(_("paid gross grater than gross weight "))
            move.write({'gross_weight': move.gross_weight -  move.paid_gross ,'quantity': move.quantity - pure , 'value' : (move.quantity - pure) * move.gold_rate  })
            move.write({'paid_gross': 0.00 ,'paid_pure' : 0.00})
            if move.gross_weight == 0.00:
                move.write({'is_full_paid': True })
            
        
        account_move.write({'pure_wt_value': account_move.pure_wt_value - pure }) 
        # pure_money = account_move.pure_wt_value * account_move.gold_rate_value
        # account_move.write({'make_value_move': account_move.make_value_move - pure_money }) 
        
        if account_move.pure_wt_value <= 0.00 and account_move.make_value_move == 0.00:
            account_move.write({'invoice_payment_state': "paid"}) 

        if not purchase_order.order_type.stock_picking_type_id :
            raise UserError(_("fill picking type field in po purhcase type"))
        rate = 0.00
        for line in purchase_order.order_line:
            if line.gold_rate > 0.00:
                rate = line.gold_rate

        if pure > 0.00:
            picking = self.env['stock.picking'].create({
                        'location_id': purchase_order.order_type.stock_picking_type_id.default_location_src_id.id,
                        'location_dest_id': purchase_order.order_type.stock_picking_type_id.default_location_dest_id.id,
                        'picking_type_id': purchase_order.order_type.stock_picking_type_id.id,
                        'bill_unfixed': account_move.id,
                        'immediate_transfer': False,
                        'move_lines': [(0, 0, {
                                'name': "unfixed move",
                                'location_id': purchase_order.order_type.stock_picking_type_id.default_location_src_id.id,
                                'location_dest_id': purchase_order.order_type.stock_picking_type_id.default_location_dest_id.id,
                                'product_id': product_id.id,
                                'product_uom': product_id.uom_id.id,
                                'picking_type_id':  purchase_order.order_type.stock_picking_type_id.id,
                                'product_uom_qty': 1,
                                'gold_rate' : rate ,
                                'pure_weight': pure,
                                'gross_weight': gross_weight ,
                                'purity': purity,})]
                    })
            account_move.write({'unfixed_stock_picking' : picking.id})
                            
        return {'type': 'ir.actions.act_window_close'}
