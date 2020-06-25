# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    gold = fields.Boolean(string='Is Gold')

    def _compute_weight_uom_name(self):
        for template in self:
            if template.gold:
                template.weight_uom_name = template.uom_po_id and \
                                           template.uom_po_id.display_name or \
                                           template.uom_id and \
                                           template.uom_id.display_name or 'g'
            else:
                template.weight_uom_name = self._get_weight_uom_name_from_ir_config_parameter()

    @api.depends('product_variant_ids', 'product_variant_ids.weight')
    def _compute_weight(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            if template.gold and (template.weight <= 0) and \
                    template.product_variant_ids.weight <= 0.0:
                raise ValidationError(
                    _('Product weight must be greater than zero.'))
                template.weight = template.product_variant_ids.weight
        for template in (self - unique_variants):
            template.weight = 0.0


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        res.weight = res.weight <= 0 and res.product_tmpl_id.weight or res.weight
        if res.gold and res.weight <= 0.0:
            raise ValidationError('Product weight must be greater than zero.')
        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        for rec in self:
            if (vals.get('gold', False) or rec.gold) and (
                    vals.get('weight') and vals.get('weight') <= 0.0 or
                    rec.weight <= 0.0):
                raise ValidationError(
                    'Product weight must be greater than zero.')
        return res


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
