# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    gold_rate = fields.Float(string='Gold Rate', digits=(12, 12))

    @api.onchange('currency_id', 'date_order')
    def get_gold_rate(self):
        if self.date_order and self.currency_id and self.currency_id.is_gold:
            print ('----------test-----------', self.date_order,
                   self.date_order.date())
            rates = self.env['gold.rates'].search([
                ('currency_id', '=', self.currency_id.id),
                ('name', '=', self.date_order.date()),
                ('company_id', 'in', [False, self.company_id and
                                      self.company_id.id or False])
            ], limit=1, order='name desc, id desc')
            if rates:
                self.gold_rate = rates[0].rate
        else:
            self.gold_rate = 0.00