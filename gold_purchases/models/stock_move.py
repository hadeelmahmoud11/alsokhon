# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round, float_is_zero



class ItemCategory(models.Model):
    _name = 'item.category'
    _description = "Item Category"

    name = fields.Char('Name')
    sub_category_lines = fields.One2many('item.category.line',
                                         'parent_category_id',
                                         string="Sub Category")


class SubCategory(models.Model):
    _name = 'item.category.line'
    _description = "Sub Category"

    name = fields.Char('Name')
    parent_category_id = fields.Many2one('item.category',
                                         string="Parent Category")


class StockMove(models.Model):
    _inherit = 'stock.move'

    gross_weight = fields.Float(string='Gross Weight', digits=(16, 3))
    pure_weight = fields.Float('Pure Weight', digits=(16, 3))
    purity = fields.Float(string="Purity", digits=(16, 3))
    gold_rate = fields.Float(string='Gold Rate', digits=(16, 3))
    item_category_id = fields.Many2one('item.category', string="Item Category")
    sub_category_id = fields.Many2one('item.category.line',
                                      string="Sub Category")
    selling_karat_id = fields.Many2one('product.attribute.value',
                                       string="Selling Karat")
    selling_making_charge = fields.Monetary('Selling Making Charge',
                                            currency_field='company_currency_id',
                                            digits=(16, 3))
    company_currency_id = fields.Many2one('res.currency',
                                          string="Company Currency",
                                          related='company_id.currency_id')


    def _create_in_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_in_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(
                    valued_move_line.qty_done, move.product_id.uom_id)
            unit_cost = abs(
                move._get_price_unit())  # May be negative (i.e. decrease an out move).
            if move.product_id.cost_method == 'standard':
                unit_cost = move.product_id.standard_price
            # Check Gold Product and pass gold rate, pure weight instead of
            # cost, qty
            if move.product_id.gold:
                svl_vals = move.product_id._prepare_in_svl_vals(
                    move.pure_weight, move.gold_rate)
            else:
                svl_vals = move.product_id._prepare_in_svl_vals(
                    forced_quantity or valued_quantity, unit_cost)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals[
                    'description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals_list.append(svl_vals)

        stock_val_layer = self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
        for layer in stock_val_layer:
            if not layer.stock_move_id.picking_id.backorder_id:
                layer.write({'value': layer.value +  layer.stock_move_id.purchase_line_id.make_value })
            layer.stock_move_id.purchase_line_id.received_gross_wt = layer.stock_move_id.purchase_line_id.received_gross_wt + layer.stock_move_id.gross_weight
        return stock_val_layer


#    def _create_out_svl(self, forced_quantity=None):
 #       """Create a `stock.valuation.layer` from `self`.

  #      :param forced_quantity: under some circunstances, the quantity to value is different than
  #          the initial demand of the move (Default value = None)
  #      """
        #svl_vals_list = []
        #for move in self:
         #   move = move.with_context(force_company=move.company_id.id)
          #  valued_move_lines = move._get_out_move_lines()
          #  valued_quantity = 0
          #  for valued_move_line in valued_move_lines:
          #      valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
         #   if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
         #       continue
             # Check Gold Product and pass gold rate, pure weight instead of
            # cost, qty
         #   if move.product_id.gold:
         #       svl_vals = move.product_id._prepare_out_svl_vals(move.pure_weight, move.company_id)
         #       svl_vals['unit_cost'] = 0.00
         #       svl_vals['quantity'] = 0.00
         #       svl_vals['value'] = 0.00
         #   else:
         #       svl_vals = move.product_id._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)
         #   svl_vals.update(move._prepare_common_svl_vals())
         #   if forced_quantity:
         #       svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name

         #   svl_vals_list.append(svl_vals)
        ##return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)


    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done()
        self.product_id.compute_available_gold()
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.onchange('lot_id', 'gross_weight')
    def change_lot(self):
        if self.lot_id:
            if self.lot_id.product_id and self.lot_id.product_id.categ_id.is_scrap:
                self.lot_id.write({
                'gross_weight': 0.0,
                'purity': 0.0
                })
                self.lot_id.write({
                'gross_weight': self.gross_weight,
                'purity': self.purity
                })
            elif self.lot_id.product_id and not self.lot_id.product_id.categ_id.is_scrap:
                self.lot_id.write({
                'gross_weight': 0.0,
                'purity': 0.0
                })
                self.lot_id.write({
                'gross_weight': self.lot_id.gross_weight + self.gross_weight,
                'purity': self.purity
                })
    image = fields.Binary()
    # related='actual_gross_weight',

    gross_weight = fields.Float(string='Gross Weight', store=True)
                                # related='move_id.gross_weight',

    actual_gross_weight = fields.Float(string='Gross Weight', store=True)

    purity = fields.Float(related="move_id.purity", string="Purity", store=True)
    pure_weight = fields.Float(compute='get_pure_weight', string="Pure Weight",
                               store=True, digits=(16, 3))
    item_category_id = fields.Many2one('item.category', string="Item Category")
    sub_category_id = fields.Many2one('item.category.line',
                                      string="Sub Category")
    selling_karat_id = fields.Many2one('product.attribute.value',
                                       string="Selling Karat",
                                       compute='get_karat')
    selling_making_charge = fields.Monetary('Selling Making Charge',
                                            digits=(16, 3))
    currency_id = fields.Many2one('res.currency', string="Company Currency",
                                  related='company_id.currency_id')



    @api.depends('move_id')
    def get_karat(self):
        for rec in self:
            rec.selling_karat_id = rec.move_id and \
                                   rec.move_id.selling_karat_id and \
                                   rec.move_id.selling_karat_id.id or False

    # @api.constrains('gross_weight')
    # def validate_gross_weight(self):
    #     for record in self:
    #         if record.gross_weight > record.actual_gross_weight:
    #             raise ValidationError(_(" The total Gross Weight for %s Can Not exceed the Gross Wt on the Purchase Order line.")%record.lot_name)

    @api.depends('gross_weight', 'purity')
    def get_pure_weight(self):
        for rec in self:
            rec.pure_weight = rec.gross_weight * (rec.purity / 1000.000)


    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        if vals.get('lot_id', False):
            for move_line in self:
                if move_line.product_id and move_line.product_id.gold:
                    lot_rec = self.env['stock.production.lot'].search(
                        [('id', '=', vals.get('lot_id'))])
                    lot_rec.gross_weight = move_line.gross_weight
                    lot_rec.purity = move_line.purity
                    lot_rec.pure_weight = move_line.pure_weight
                    lot_rec.item_category_id = move_line.item_category_id.id if \
                        move_line.item_category_id else False
                    lot_rec.sub_category_id = move_line.sub_category_id.id if \
                        move_line.sub_category_id else False
                    lot_rec.selling_making_charge = \
                        move_line.selling_making_charge if \
                            move_line.selling_making_charge else False
                    lot_rec.selling_karat_id = move_line.selling_karat_id.id if \
                        move_line.selling_karat_id else False

        # if vals.get('gross_weight', False):
        #     for move_line_gross in self:
        #         move_line_gross.move_id.write({'gross_weight':  vals.get('gross_weight')})
        #         move_line_gross.move_id.write({'pure_weight':  vals.get('gross_weight') * (self.purity / 1000.000) })

        return res

    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)
        # if vals.get('gross_weight', False):
        #     if vals.get('move_id'):
        #         stock_move = self.env['stock.move'].browse([vals.get('move_id')])
        #         stock_move.write({'gross_weight':  vals.get('gross_weight')})
        #         stock_move.write({'pure_weight':  vals.get('gross_weight') * (stock_move.purity / 1000.000) })

        return res

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    gross_weight = fields.Float('Gross Weight', digits=(16, 3))
    pure_weight = fields.Float('Pure Weight', digits=(16, 3))


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    pure_weight = fields.Float('Pure Weight', digits=(16, 3))
    gold_rate = fields.Float(string='Gold Rate', digits=(16, 3))
    gross_weight = fields.Float('Gross Weight',related="stock_move_id.gross_weight" ,  store=True,digits=(16, 3))
    purity = fields.Float(related="stock_move_id.purity" , string="purity", store=True,digits=(16, 3))
    is_scrap = fields.Boolean(related="product_id.categ_id.is_scrap" , string="scrap", store=True)
    qty_done = fields.Float(related="stock_move_id.product_qty" , string="product_qty", store=True)
    picking_id = fields.Many2one('stock.picking',related="stock_move_id.picking_id" , string="picking_id", store=True)
    is_full_paid = fields.Boolean(string="full paid")
    paid_pure = fields.Float(string="Paid Pure", digits=(16, 3))
    paid_gross = fields.Float(string="Paid Gross", digits=(16, 3))

    @api.onchange('paid_gross')
    def onchange_paid_gross(self):
        for rec in self:
            rec.write({'paid_pure': rec.paid_gross  *  (rec.stock_move_id.purity / 1000)})


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override to handle the "inventory mode" and set the `inventory_quantity`
        in view list grouped.
        """
        if 'purity' in fields:
            fields.remove('purity')
        result = super(StockValuationLayer, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        return result
