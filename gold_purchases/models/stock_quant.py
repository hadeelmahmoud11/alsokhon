""" init object stock.quant """

import logging

from odoo import fields, models, api

LOGGER = logging.getLogger(__name__)


class StockQuant(models.Model):
    """ init object stock.quant """
    _inherit = 'stock.quant'

    move_line_id = fields.Many2one(comodel_name="stock.move.line",
                                   compute="_compute_move_line_values",
                                   string="Move Line", )
    gross_weight = fields.Float(compute="_compute_move_line_values",
                                string='Gross Weight', )
    purity = fields.Float(string="Purity",
                          compute="_compute_move_line_values", )
    pure_weight = fields.Float(string="Pure Weight", digits=(16, 3),
                               compute="_compute_move_line_values", )

    item_category_id = fields.Many2one('item.category', string="Item Category",
                                       compute="_compute_move_line_values", )
    sub_category_id = fields.Many2one('item.category.line',
                                      string="Sub Category",
                                      compute="_compute_move_line_values", )
    selling_karat_id = fields.Many2one('product.attribute.value',
                                       string="Selling Karat",
                                       compute="_compute_move_line_values", )
    selling_making_charge = fields.Monetary('Selling Making Charge',
                                            digits=(16, 3),
                                            compute="_compute_move_line_values", )

    @api.depends('lot_id', 'product_id')
    def _compute_move_line_values(self):
        """
        Compute move_line_id
        """
        for rec in self:
            gross_weight = 0
            purity = 0
            pure_weight = 0
            item_category_id = self.env['item.category']
            sub_category_id = self.env['item.category.line']
            selling_karat_id = self.env['product.attribute.value']
            selling_making_charge = 0
            move_line_id = self.env['stock.move.line']
            if rec.lot_id and rec.product_id:
                move_line_id = move_line_id.search([
                    ('lot_id', '=', rec.lot_id.id),
                    ('product_id', '=', rec.product_id.id)
                ])
                if move_line_id:
                    gross_weight = move_line_id.gross_weight
                    purity = move_line_id.purity
                    pure_weight = move_line_id.pure_weight
                    item_category_id = move_line_id.item_category_id
                    sub_category_id = move_line_id.sub_category_id
                    selling_karat_id = move_line_id.selling_karat_id
                    selling_making_charge = move_line_id.selling_making_charge
            rec.gross_weight = gross_weight
            rec.purity = purity
            rec.pure_weight = pure_weight
            rec.item_category_id = item_category_id
            rec.sub_category_id = sub_category_id
            rec.selling_karat_id = selling_karat_id
            rec.selling_making_charge = selling_making_charge
            rec.move_line_id = move_line_id
