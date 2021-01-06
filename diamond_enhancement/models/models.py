# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round, float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    carat = fields.Float('Diamond Carat')
    carat_wt = fields.Float('Diamond Wt')

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    carat = fields.Float('Diamond Carat')
    carat_wt = fields.Float('Diamond Carat Wt')