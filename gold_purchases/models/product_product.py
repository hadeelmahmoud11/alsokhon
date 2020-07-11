# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    available_gold = fields.Float('Available Gold', digits=(16, 3))

    def compute_available_gold(self):
        stock_move_line_env = self.env['stock.move.line']
        lot_env = self.env['stock.production.lot']
        for record in self.filtered(lambda x: x.type == 'product' and x.gold):
            sml_ids = stock_move_line_env.search(
                [('product_id', '=', record.id), ('state', '=', 'done')])
            total_qty = 0.0
            for sml_id in sml_ids:
                if sml_id.picking_id and sml_id.picking_id.picking_type_id and \
                        sml_id.picking_id.picking_type_id.code:
                    code = sml_id.picking_id.picking_type_id.code
                    if code == 'incoming':
                        if sml_id.lot_id:
                            lots = lot_env.search(
                                [('id', '=', sml_id.lot_id.id)])
                            for lot in lots:
                                total_qty += lot.pure_weight
                        else:
                            total_qty += sml_id.pure_weight
                    elif code == 'outgoing':
                        if sml_id.lot_id:
                            lots = lot_env.search(
                                [('id', '=', sml_id.lot_id.id)])
                            for lot in lots:
                                total_qty -= lot.pure_weight
                        else:
                            total_qty -= sml_id.pure_weight
            record.available_gold = total_qty
