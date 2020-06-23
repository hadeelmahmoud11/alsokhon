# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItemCategory(models.Model):
    _name = 'item.category'
    _description = "Item Category"

    name = fields.Char('Name')
    sub_category_lines = fields.One2many('item.category.line',
                                         'parent_category_id',
                                         string="Sub Category")


class SubCategory(models.Model):
    _name = 'item.category.line'
    _description = "Sub Category"

    name = fields.Char('Name')
    parent_category_id = fields.Many2one('item.category',
                                         string="Parent Category")


class StockMove(models.Model):
    _inherit = 'stock.move'

    gross_weight = fields.Float(string='Gross Weight')
    pure_weight = fields.Float('Pure Weight')
    purity = fields.Float(string="Purity")
    item_category_id = fields.Many2one('item.category', string="Item Category")
    sub_category_id = fields.Many2one('item.category.line',
                                      string="Sub Category")
    selling_karat_id = fields.Many2one('product.attribute.value',
                                       string="Selling Karat")
    selling_making_charge = fields.Monetary('Selling Making Charge',
                                            currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency',
                                          string="Company Currency",
                                          related='company_id.currency_id')

    # product_template_attribute_value_ids = fields.Many2many(
    #     'product.template.attribute.value',
    #     'stock_move_product_attribute_value_rel', 'move_id', 'value_id',
    #     compute='get_attribute_ids')
    #
    # def get_attribute_ids(self):
    #     for rec in self:
    #         rec.product_template_attribute_value_ids = rec.product_id and rec.product_id.product_template_attribute_value_ids and [
    #             (6, 0,
    #              rec.product_id.product_template_attribute_value_ids.ids)] or False
    # def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
    #     res = super(StockMove, self)._prepare_move_line_vals()
    #     res.update({
    #         'gross_weight': self.gross_weight,
    #         'purity': self.purity,
    #         'pure_weight': self.pure_weight,
    #         'item_category_id': self.item_category_id.id if self.item_category_id else False,
    #         'sub_category_id': self.sub_category_id.id if self.sub_category_id else False,
    #         'selling_making_charge': self.selling_making_charge,
    #         'selling_karat_id': self.selling_karat_id.id if self.selling_karat_id else False,
    #     })
    #     return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gross_weight = fields.Float(related='actual_gross_weight',
                                string='Gross Weight', store=True)
    actual_gross_weight = fields.Float(related='move_id.gross_weight',
                                       string='Gross Weight', store=True)
    purity = fields.Float(related="move_id.purity", string="Purity", store=True)
    pure_weight = fields.Float(compute='get_pure_weight', string="Pure Weight",
                               store=True)
    item_category_id = fields.Many2one('item.category', string="Item Category")
    sub_category_id = fields.Many2one('item.category.line',
                                      string="Sub Category")
    selling_karat_id = fields.Many2one('product.attribute.value',
                                       string="Selling Karat")
    selling_making_charge = fields.Monetary('Selling Making Charge')
    currency_id = fields.Many2one('res.currency', string="Company Currency",
                                  related='company_id.currency_id')

    # @api.constrains('gross_weight')
    # def validate_gross_weight(self):
    #     for record in self:
    #         if record.gross_weight > record.actual_gross_weight:
    #             raise ValidationError(_(" The total Gross Weight for %s Can Not exceed the Gross Wt on the Purchase Order line.")%record.lot_name)

    @api.depends('gross_weight', 'purity')
    def get_pure_weight(self):
        for rec in self:
            rec.pure_weight = rec.gross_weight * (rec.purity / 1000.000)

    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        if vals.get('lot_id', False):
            for move_line in self:
                if move_line.product_id and move_line.product_id.gold:
                    lot_rec = self.env['stock.production.lot'].search(
                        [('id', '=', vals.get('lot_id'))])
                    lot_rec.gross_weight = move_line.gross_weight
                    lot_rec.purity = move_line.purity
                    lot_rec.pure_weight = move_line.pure_weight
                    lot_rec.item_category_id = move_line.item_category_id.id if \
                        move_line.item_category_id else False
                    lot_rec.sub_category_id = move_line.sub_category_id.id if \
                        move_line.sub_category_id else False
                    lot_rec.selling_making_charge = \
                        move_line.selling_making_charge if \
                            move_line.selling_making_charge else False
                    lot_rec.selling_karat_id = move_line.selling_karat_id.id if \
                        move_line.selling_karat_id else False
        return res


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    gross_weight = fields.Float('Gross Weight')
    pure_weight = fields.Float('Pure Weight')
