# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit= "product.template"

    gold = fields.Boolean(string='Is Gold')

    def _compute_weight_uom_name(self):
        for template in self:
            if template.gold:
                template.weight_uom_name = template.uom_po_id and \
                                           template.uom_po_id.display_name or\
                                           template.uom_id and \
                                           template.uom_id.display_name or 'g'
            else:
                template.weight_uom_name = self._get_weight_uom_name_from_ir_config_parameter()


class ProductProduct(models.Model):
    _inherit= "product.product"

    @api.model
    def create(self,vals):
        res = super(ProductProduct, self).create(vals)
        if res.gold and res.weight <= 0.0:
            raise ValidationError('Product Weight Must Be Greater than zero.')
        return res

    def write(self,vals):
        res = super(ProductProduct, self).write(vals)
        for rec in self:
            if (vals.get('gold') and vals.get('gold') == True or rec.gold) and (vals.get('weight') and vals.get('weight') <= 0.0 or rec.weight <= 0.0):
                raise ValidationError('Product Weight Must Be Greater than zero.')
        return res
