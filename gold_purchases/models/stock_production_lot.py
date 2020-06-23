# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    gross_weight = fields.Float(string="Gross Weight")
    purity = fields.Float(string="Purity")
    pure_weight = fields.Float(compute='get_pure_weight',string="Pure Weight")
    item_category_id = fields.Many2one('item.category',string="Item Category")
    sub_category_id = fields.Many2one('item.category.line', string="Sub Category")
    selling_karat_id = fields.Many2one('product.attribute.value', string="Selling Karat")
    selling_making_charge = fields.Monetary('Selling Making Charge')
    currency_id = fields.Many2one('res.currency', string="Company Currency", related='company_id.currency_id')

    @api.depends('gross_weight', 'purity')
    def get_pure_weight(self):
        for rec in self:
            rec. pure_weight = rec.gross_weight * rec.purity / 1000