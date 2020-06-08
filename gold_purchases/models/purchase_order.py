# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    period_from = fields.Float('Period From')
    period_to = fields.Float('Period To')
    period_uom_id = fields.Many2one('uom.uom', 'Period UOM')

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res.update({
            'period_from': self.period_from,
            'period_to': self.period_to,
            'period_uom_id': self.period_uom_id and self.period_uom_id.id or False
        })
        return res
