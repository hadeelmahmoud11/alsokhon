# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round, float_is_zero

class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_diamond = fields.Boolean('Diamond')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    diamond = fields.Boolean(string='Gold')
    is_diamond_making_charges = fields.Boolean(string='Is Making Charges')
    making_charge_diamond_id = fields.Many2one('product.product', 'Making Charges product')








class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    carat = fields.Char('Diamond Carat')
    d_make_value = fields.Char('Diamond Labor Charges')

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    carat = fields.Char('Diamond Carat')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    carat = fields.Char('Diamond Carat')
    d_make_value = fields.Char('Diamond Labor Charges')

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    carat = fields.Char('Diamond Carat')


class StockMove(models.Model):
    _inherit = 'stock.move'

    carat = fields.Char('Diamond Carat')

class StockMove(models.Model):
    _inherit = 'stock.move.line'
    carat = fields.Char('Diamond Carat')


class AccountMove(models.Model):
    _inherit = 'account.move.line'
    carat = fields.Char('Diamond Carat')
