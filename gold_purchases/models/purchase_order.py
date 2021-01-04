# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date , timedelta , datetime
from odoo.exceptions import ValidationError,UserError



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_gold_vale_order = fields.Float('Total Gold Value', compute="_compute_total_gold_value_order")
    def _compute_total_gold_value_order(self):
        for this in self:
            total = 0.0
            for line in this.order_line:
                if line.product_id.is_making_charges:
                    total = total
                else:
                    total = total+line.price_subtotal
            this.total_gold_vale_order = total
    total_make_vale_order = fields.Float('Total Make Value', compute="_compute_total_make_value_order")
    def _compute_total_make_value_order(self):
        for this in self:
            total = 0.0
            for line in this.order_line:
                if line.product_id.is_making_charges:
                    total = total+line.price_subtotal
                else:
                    total = total
            this.total_make_vale_order = total

    period_from = fields.Float('Period From')
    period_to = fields.Float('Period To')
    period_uom_id = fields.Many2one('uom.uom', 'Period UOM')
    is_gold_fixed = fields.Boolean(string='Is Gold Fixed',
                                   compute='check_gold_fixed')
    stock_move_id = fields.Many2one('account.move', string='Stock Entry – Gold')
    bill_move_id = fields.Many2one('account.move', string='Bill Entry - Gold')

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        if self.order_type.is_fixed:
            result['context'] = {
                'default_type': 'in_invoice',
                'default_company_id': self.company_id.id,
                'default_purchase_id': self.id,
                'default_purchase_type': "fixed",
            }
        elif  self.order_type.gold:
            result['context'] = {
                'default_type': 'in_invoice',
                'default_company_id': self.company_id.id,
                'default_purchase_id': self.id,
                'default_purchase_type': "unfixed",
            }
        else:
            result['context'] = {
                'default_type': 'in_invoice',
                'default_company_id': self.company_id.id,
                'default_purchase_id': self.id,
            }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        print("+++++++++++++++++++++++++++++++++++++++++")
        print(result)
        print("+++++++++++++++++++++++++++++++++++++++++")
        return result

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        res.update({
            'period_from': self.period_from,
            'period_to': self.period_to,
            'period_uom_id': self.period_uom_id and self.period_uom_id.id or False
        })
        if self.order_type.gold and self.order_type.is_unfixed:
            res.update({'purchase_type':'unfixed'})
        elif self.order_type.gold and self.order_type.is_fixed:
            res.update({'purchase_type':'fixed'})
        return res

    @api.depends('order_type')
    def check_gold_fixed(self):
        for rec in self:
            rec.is_gold_fixed = rec.order_type and \
                                rec.order_type.is_fixed or rec.order_type.is_unfixed and \
                                rec.order_type.gold and True or False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Unit Price', required=True,
                              digits='Product Price', copy=False, default=0)
    gross_wt = fields.Float('Gross Wt', digits=(16, 3))
    total_gross_wt = fields.Float('Total Gross', compute='_get_gold_rate' ,digits=(16, 3))
    received_gross_wt = fields.Float('received Gross Wt', digits=(16, 3))
    purity_id = fields.Many2one('gold.purity', 'Purity')
    pure_wt = fields.Float('Pure Wt', compute='_get_gold_rate', digits=(16, 3))
    purity_hall = fields.Float('Purity H', digits=(16, 3))
    purity_diff = fields.Float('Purity +/-', digits=(16, 3))
    total_pure_weight = fields.Float('Pure Weight', compute='_get_gold_rate',
                                     digits=(16, 3))

    def _get_gold_stock(self):
        for this in self:
            if this.product_id:
                location = self.env['stock.location'].search([('usage','=','internal')])
                quants = self.env['stock.quant'].search([('product_id','=',this.product_id.id),('location_id','=',location[0].id)])
                total = 0.0
                for quant in quants:
                    # print(quant.lot_id.name)
                    # print(quant.inventory_quantity)
                    total = total + quant.inventory_quantity
                this.stock = total
    stock = fields.Float('Stock', compute='_get_gold_stock', digits=(16, 3))
    make_rate = fields.Monetary('Make Rate/G', digits=(16, 3))
    make_value = fields.Monetary('Make Value', compute='_get_gold_rate',
                                 digits=(16, 3))
    gold_rate = fields.Float('Gold Rate/G', compute='_get_gold_rate',
                             digits=(16, 3))
    gold_value = fields.Monetary('Gold Value', compute='_get_gold_rate',
                                 digits=(16, 3))
    is_make_value = fields.Boolean(string='is_make_value')
    total_with_make = fields.Float('Total Value + Make Value', compute="_compute_total_with_make")
    def _compute_total_with_make(self):
        for this in self:
            if this.product_id.is_making_charges:
                this.total_with_make = 0.0
            else:
                this.total_with_make = this.price_subtotal +this.make_value

    @api.onchange('purity_hall','product_qty')
    def onchange_purity_hall(self):
        for rec in self:
            if rec.purity_hall > 1000 or rec.purity_hall < 0.00 :
                raise ValidationError(_('purity hallmark between 1 - 1000'))

            rec.purity_diff = ( rec.product_qty * (rec.purity_hall - rec.purity_id.purity)) / 100

    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        if vals.get('make_rate'):
            if vals.get('make_rate') > 0.00 and len(self.order_id.order_line) == 1 :
                product_object = self.env['product.product'].browse([self.product_id.id])
                make_value_product = product_object.making_charge_id
                uom = self.env.ref('uom.product_uom_unit')
                make = self.env['purchase.order.line'].create({
                                        'product_id': make_value_product.id,
                                        'name': make_value_product.name,
                                        'product_qty': 1,
                                        'price_unit': 0.00,
                                        'product_uom': uom.id,
                                        'order_id':self.order_id.id,
                                        'date_planned': datetime.today() ,
                                        'is_make_value': True,
                                        'price_subtotal': 0.00,
                                    })
        return res

    @api.onchange('product_qty')
    def update_gross(self):
        if self.product_id and self.product_id.scrap and self.product_qty:
            self.gross_wt = self.product_qty
    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)

        if vals.get('product_id'):
            product_object = self.env['product.product'].browse([vals.get('product_id')])
            if product_object.gold and not product_object.scrap:
                if not  product_object.making_charge_id.id :
                    raise ValidationError(_('Please fill make value product for this product'))

                make_value_product = product_object.making_charge_id
                uom = self.env.ref('uom.product_uom_unit')
                if vals.get('make_rate') > 0.00:
                    make = self.env['purchase.order.line'].create({
                                        'product_id': make_value_product.id,
                                        'name': make_value_product.name,
                                        'product_qty': 1,
                                        'price_unit': 0.00,
                                        'product_uom': uom.id,
                                        'order_id': vals.get('order_id'),
                                        'date_planned': datetime.today() ,
                                        'is_make_value': True,
                                        'price_subtotal': 0.00,
                                    })
        return res



    @api.depends('product_id', 'product_qty', 'price_unit', 'gross_wt',
                 'purity_id', 'purity_diff', 'make_rate',
                 'order_id', 'order_id.order_type', 'order_id.currency_id')
    def _get_gold_rate(self):
        for rec in self:
            if rec.product_id.making_charge_id.id:
                make_value_product = self.env['product.product'].browse([rec.product_id.making_charge_id.id])
                product_make_object = self.env['purchase.order.line'].search([('order_id','=',rec.order_id.id),('product_id','=',make_value_product.id)])
            if rec.product_id.categ_id.is_scrap:
                rec.pure_wt = rec.gross_wt * (rec.purity_id and (
                        rec.purity_id.scrap_purity / 1000.000) or 0)
            else:
                rec.pure_wt = rec.product_qty * rec.gross_wt * (rec.purity_id and (
                        rec.purity_id.purity / 1000.000) or 0)
            rec.total_pure_weight = rec.pure_wt + rec.purity_diff
            # NEED TO ADD PURITY DIFF + rec.purity_diff
            new_pure_wt = rec.pure_wt + rec.purity_diff
            rec.stock = (rec.product_id and rec.product_id.available_gold or
                         0.00) + new_pure_wt

            rec.make_value = rec.product_qty * rec.gross_wt * rec.make_rate
            rec.gold_rate = rec.order_id.gold_rate / 1000.000000000000
            rec.gold_value = rec.gold_rate and (
                    rec.total_pure_weight * rec.gold_rate) or 0
            if rec.product_id.scrap:
                rec.total_gross_wt = rec.product_qty
            else:
                rec.total_gross_wt = rec.gross_wt * rec.product_qty


            make_value_product = self.env['product.product'].browse([rec.product_id.making_charge_id.id])
            product_basic_line = self.env['purchase.order.line'].search([('order_id','=',rec.order_id.id),('product_id','=',make_value_product.id)])
            for line in product_basic_line:
                product_make_object.write({'gold_rate' : 0.00 ,'price_subtotal' : rec.make_value ,'price_unit':rec.make_value})



    @api.depends('product_qty', 'price_unit', 'taxes_id', 'gross_wt',
                 'purity_id', 'purity_diff', 'make_rate',
                 'order_id', 'order_id.order_type',
                 'order_id.state', 'order_id.order_type.gold')
    def _compute_amount(self):
        for line in self:
            if line.order_id and (line.order_id.order_type.is_fixed or line.order_id.order_type.gold) and \
                    line.product_id.gold:
                taxes = line.taxes_id.compute_all(
                    line.gold_value,
                    line.order_id.currency_id,
                    1,
                    line.product_id,
                    line.order_id.partner_id)
                line.update({
                    'price_tax': sum(
                        t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                    'price_unit': 0
                })
            else:
                vals = line._prepare_compute_all_values()
                taxes = line.taxes_id.compute_all(
                    vals['price_unit'],
                    vals['currency_id'],
                    vals['product_qty'],
                    vals['product'],
                    vals['partner'])
                line.update({
                    'price_tax': sum(
                        t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if self.product_id and self.product_id.scrap:
            res and res[0].update({
                'gross_weight': self.gross_wt,
                'pure_weight': self.pure_wt,
                'purity': self.purity_id.scrap_purity or 1,
                'gold_rate': self.gold_rate,
                'selling_karat_id':
                    self.product_id.product_template_attribute_value_ids and
                    self.product_id.product_template_attribute_value_ids.mapped(
                        'product_attribute_value_id')[0].id or
                    False
            })
        else:
            res and res[0].update({
                'gross_weight': self.gross_wt * self.product_qty,
                'pure_weight': self.pure_wt,
                'purity': self.purity_id.purity or 1,
                'gold_rate': self.gold_rate,
                'selling_karat_id':
                    self.product_id.product_template_attribute_value_ids and
                    self.product_id.product_template_attribute_value_ids.mapped(
                        'product_attribute_value_id')[0].id or
                    False
            })
        print(res)
        return res

    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        #make_value_product = self.env.ref('gold_purchases.make_value_product')
        product_object = self.env['product.product'].browse([res.get('product_id')])

        price_un = 0.00
        diff_gross = 0.00
        if product_object.is_making_charges:
            price_un = res.get('price_unit')
        if product_object.gold:
            if product_object.purchase_method == "receive":
                if self.received_gross_wt < (self.gross_wt * self.product_qty):
                    total_pure_weight = self.received_gross_wt * (self.purity_id and (
                        self.purity_id.purity / 1000.000) or 1)
                    try:
                        diff_gross =  (self.gross_wt * self.product_qty) / self.received_gross_wt
                    except:
                        raise UserError(_('You Should Receive Quantities First'))
                    new_pure = total_pure_weight / self.product_qty
                    new_purity_diff =  self.purity_diff / self.product_qty
                    res.update({
                        'gross_wt': self.received_gross_wt ,
                        'pure_wt': new_pure - new_purity_diff ,
                        'purity_id': self.purity_id and self.purity_id.id or False,
                        'purity_diff': new_purity_diff,
                        'gold_rate': self.gold_rate,
                        'make_rate': self.make_rate,
                        'make_value': self.make_value / diff_gross ,
                        'gold_value': self.gold_rate and (new_pure * self.gold_rate) or 0,
                        'price_unit': self.gold_rate and (new_pure * self.gold_rate) or 0 ,
                    })
                else:
                    res.update({
                        'gross_wt': self.gross_wt,
                        'pure_wt': self.pure_wt,
                        'purity_id': self.purity_id and self.purity_id.id or False,
                        'purity_diff': self.purity_diff,
                        'gold_rate': self.gold_rate,
                        'make_rate': self.make_rate,
                        'make_value': self.make_value,
                        'gold_value': self.gold_value,
                        'price_unit': self.gold_value / self.product_qty   ,
                    })
            else:
                # if self.product_qty < (self.gross_wt * self.product_qty):
                #     total_pure_weight = self.product_qty * (self.purity_id and (
                #         self.purity_id.purity / 1000.000) or 1)
                #     try:
                #         diff_gross =  (self.gross_wt * self.product_qty) / self.product_qty
                #     except:
                #         raise UserError(_('You Should Receive Quantities First'))
                #     new_pure = total_pure_weight / self.product_qty
                #     new_purity_diff =  self.purity_diff / self.product_qty
                #     res.update({
                #         'gross_wt': self.received_gross_wt ,
                #         'pure_wt': new_pure - new_purity_diff ,
                #         'purity_id': self.purity_id and self.purity_id.id or False,
                #         'purity_diff': new_purity_diff,
                #         'gold_rate': self.gold_rate,
                #         'make_rate': self.make_rate,
                #         'make_value': self.make_value / diff_gross ,
                #         'gold_value': self.gold_rate and (new_pure * self.gold_rate) or 0,
                #         'price_unit': self.gold_rate and (new_pure * self.gold_rate) or 0 ,
                #     })
                # else:
                res.update({
                    'gross_wt': self.gross_wt,
                    'pure_wt': self.pure_wt,
                    'purity_id': self.purity_id and self.purity_id.id or False,
                    'purity_diff': self.purity_diff,
                    'gold_rate': self.gold_rate,
                    'make_rate': self.make_rate,
                    'make_value': self.make_value,
                    'gold_value': self.gold_value,
                    'price_unit': self.gold_value / self.product_qty   ,
                })
        product_object = self.env['product.product'].browse([res.get('product_id')])
        make_value_product = product_object.making_charge_id
        if product_object.is_making_charges:
            purchase_order = self.env['purchase.order'].browse([self.order_id.id])
            new_gross_wt = 0.00
            new_product_qty = 0.00
            new_received_gross_wt =0.00
            for line in purchase_order.order_line:
                if line.product_id == self.product_id:
                    if line.product_id.purchase_method == 'receive':
                        if line.gross_wt > 0.00 and line.received_gross_wt > 0.00:
                            new_gross_wt = line.gross_wt
                            new_product_qty = line.product_qty
                            new_received_gross_wt = line.received_gross_wt
                    else:
                        if line.gross_wt > 0.00 and line.product_qty > 0.00:
                            new_gross_wt = line.gross_wt
                            new_product_qty = line.product_qty
                            new_received_gross_wt = line.received_gross_wt
                        # print(new_gross_wt)
                        # print(new_product_qty)
                        # print(new_received_gross_wt)
            if self.product_id.purchase_method == 'receive':
                print(price_un)
                print(new_gross_wt)
                print(new_product_qty)
                print(new_received_gross_wt)
                if new_received_gross_wt <=0:
                    raise ValidationError(_('You Should Receive Products First'))
                else:
                    diff_gross =  (new_gross_wt * new_product_qty) / new_received_gross_wt
                if diff_gross > 0.00:
                    res.update({'price_unit': price_un / diff_gross , 'quantity': 1.00,'gold_rate':0.00})
                else:
                    res.update({'price_unit': price_un, 'quantity': 1.00,'gold_rate':0.00})
            else:
                # if new_product_qty <=0:
                #     raise ValidationError(_('You Should Receive Products First'))
                # else:
                diff_gross =  (new_gross_wt * new_product_qty)
                if diff_gross > 0.00:
                    res.update({'price_unit': price_un / diff_gross , 'quantity': 1.00,'gold_rate':0.00})
                else:
                    res.update({'price_unit': price_un, 'quantity': 1.00,'gold_rate':0.00})



        return res
