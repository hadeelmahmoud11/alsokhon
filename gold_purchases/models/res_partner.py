# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_payable_account(self):
        asset_type = self.env.ref('account.data_account_type_payable')
        if asset_type:
            return [('user_type_id', '=', asset_type.id), ('gold', '=', True)]
        return []

    gold_account_payable_id = fields.Many2one(
        'account.account',
        domain=get_payable_account, string='Account Payable - Gold')



