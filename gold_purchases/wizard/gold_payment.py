# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class stockGoldMove(models.TransientModel):
    _name = 'stock.move.gold'
    _description = 'Generate move for all selected moves'

    move_ids = fields.Many2many('stock.move', 'move_stock_group_rel', 'stock_gold', 'move_id',  'moves', readonly=False)

    def compute_sheet(self):
        [data] = self.read()
        if not data['move_ids']:
            raise UserError(_("You must select move(s) to generate payment(s)."))

        active_id = self.env.context.get('active_id')
        if active_id:
            account_move = self.env['account.move'].search([('id' ,'=', active_id)])

        pure = 0.00
        gross_weight = 0.00
        purity = 0.00
        for move in self.env['stock.move'].browse(data['move_ids']):
            pure = pure + move.pure_weight
            gross_weight = gross_weight + move.gross_weight
            purity = purity + move.purity
            product_id = move.product_id
            location_id = move.location_id
            location_dest_id = move.location_dest_id
            
        if pure > account_move.pure_wt_value:
            raise UserError(_("you can pay in gold" + "" + str(account_move.pure_wt_value)))
        else:
            account_move.write({'pure_wt_value': account_move.pure_wt_value - pure }) 
            pure_money = account_move.pure_wt_value * account_move.gold_rate_value
            account_move.write({'make_value_move': account_move.make_value_move - pure_money }) 

        picking_type_out = self.env['ir.model.data'].xmlid_to_object('stock.picking_type_out')
        picking = self.env['stock.picking'].create({
                    'location_id': location_dest_id.id,
                    'location_dest_id': location_id.id,
                    'picking_type_id': picking_type_out.id,
                    'immediate_transfer': False
                })
            
        stock_move = self.env['stock.move'].create({
                        'name': "unfixed move",
                        'procure_method': "make_to_order",
                        'location_id': location_dest_id.id,
                        'location_dest_id': location_id.id,
                        'product_id': product_id.id,
                        'product_uom': product_id.uom_id.id,
                        'picking_id': picking.id,
                        'picking_type_id': picking_type_out.id,
                        'product_uom_qty': 1,
                        'pure_weight': pure,
                        'gross_weight': gross_weight,
                        'purity': purity,
                       
                    })
                            
        return {'type': 'ir.actions.act_window_close'}
