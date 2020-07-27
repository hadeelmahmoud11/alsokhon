# -*- coding: utf-8 -*-
from itertools import groupby
from odoo.exceptions import ValidationError
from odoo import api, fields, models , _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    period_from = fields.Float('Period From')
    period_to = fields.Float('Period To')
    period_uom_id = fields.Many2one('uom.uom', 'Period UOM')

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for rec in self.filtered(lambda x: x.state == 'done'):
            rec.create_gold_journal_entry()
        return res

    def create_gold_journal_entry(self):
        self.ensure_one()
        moves = self.move_lines.filtered(lambda x: x._is_in() and
                                                   x.product_id and
                                                   x.product_id.gold and
                                                   x.product_id.categ_id and
                                                   x.product_id.categ_id.is_gold and
                                                   x.product_id.categ_id.gold_on_hand_account)
        if moves:
            total_purity = 0
            product_dict = {}
            description = '%s' % self.name
            for product_id, move_list in groupby(moves, lambda x: x.product_id):
                description = '%s-%s' % (description, product_id.display_name)
                if product_id not in product_dict.keys():
                    product_dict[product_id] = sum(
                        x.pure_weight for x in move_list)
                else:
                    product_dict[product_id] = product_dict[product_id] + sum(
                        x.pure_weight for x in move_list)
            total_purity = sum(value for key, value in product_dict.items())
            if total_purity > 0.0 and product_dict and \
                    self.partner_id :
                if not next(iter(product_dict)).categ_id.gold_journal.id:
                    raise ValidationError(_('Please fill gold journal in product Category'))
                journal_id = next(iter(product_dict)).categ_id.gold_journal.id

                move_lines = self._prepare_account_move_line(product_dict)
                if move_lines:
                    AccountMove = self.env['account.move'].with_context(
                        default_journal_id=journal_id)
                    date = self._context.get('force_period_date',
                                             fields.Date.context_today(self))
                    new_account_move = AccountMove.sudo().create({
                        'journal_id': journal_id,
                        'line_ids': move_lines,
                        'date': date,
                        'ref': description,
                        'type': 'entry',
                    })
                    new_account_move.post()

    def _prepare_account_move_line(self, product_dict):
        debit_lines = []
        for product_id, value in product_dict.items():
            if not product_id.categ_id.gold_on_hand_account.id or not product_id.categ_id.gold_stock_input_account.id:
                raise ValidationError(_('Please fill gold accounts in product Category'))
            debit_lines.append({
                'name': '%s - %s' % (self.name, product_id.name),
                'product_id': product_id.id,
                'quantity': 1,
                'product_uom_id': product_id.uom_id.id,
                'ref': '%s - %s' % (self.name, product_id.name),
                'partner_id': self.partner_id.id,
                'debit': round(value, 3),
                'credit': 0,
                'account_id': product_id.categ_id.gold_on_hand_account.id,
            })
        credit_line = [{
            'name': '%s - %s' % (self.name, product_id.name),
            'product_id': product_id.id,
            'quantity': 1,
            'product_uom_id': product_id.uom_id.id,
            'ref': '%s - %s' % (self.name, product_id.name),
            'partner_id': self.partner_id.id,
            'debit': 0,
            'credit': sum(x['debit'] for x in debit_lines),
            'account_id': product_id.categ_id.gold_stock_input_account.id,
        }]
        res = [(0, 0, x) for x in debit_lines + credit_line]
        return res
