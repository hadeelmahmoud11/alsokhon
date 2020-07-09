# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birth_date = fields.Date('Date of Birth')

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.birth_date = False