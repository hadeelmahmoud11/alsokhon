# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    gross_weight = fields.Float('Gross Weight')
    pure_weight = fields.Float('Pure Weight')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gross_weight = fields.Float(
        related='move_id.gross_weight', string='Gross Weight')
    pure_weight = fields.Float(
        related='move_id.pure_weight', string='Pure Weight')


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    gross_weight = fields.Float('Gross Weight')
    pure_weight = fields.Float('Pure Weight')