# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPIcking(models.Model):
    _inherit = 'stock.picking'

    period_from = fields.Float('Period From')
    period_to = fields.Float('Period To')
    period_uom_id = fields.Many2one('uom.uom', 'Period UOM')
