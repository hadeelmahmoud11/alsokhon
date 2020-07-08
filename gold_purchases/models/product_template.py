# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    gold = fields.Boolean(string='Is Gold')
    origin = fields.Many2one('res.country', string='Country')

    def _compute_weight_uom_name(self):
        for template in self:
            if template.gold:
                template.weight_uom_name = template.uom_po_id and \
                                           template.uom_po_id.display_name or \
                                           template.uom_id and \
                                           template.uom_id.display_name or 'g'
            else:
                template.weight_uom_name = self._get_weight_uom_name_from_ir_config_parameter()


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def get_account_assets_type(self):
        asset_type = self.env.ref('account.data_account_type_current_assets')
        if asset_type:
            return [('user_type_id', '=', asset_type.id), ('gold', '=', True)]
        return []

    gold_journal = fields.Many2one(
        'account.journal', domain=[('gold', '=', True)],
        string='Gold Journal')
    gold_on_hand_account = fields.Many2one('account.account',
                                           domain=get_account_assets_type,
                                           string='Stock In Hand - Gold')
