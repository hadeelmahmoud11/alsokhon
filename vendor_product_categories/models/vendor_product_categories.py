from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    product_category_ids = fields.Many2many(comodel_name='product.category', string='Product Category')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_category_ids = fields.Many2many(related='partner_id.product_category_ids', string='Product Category')
