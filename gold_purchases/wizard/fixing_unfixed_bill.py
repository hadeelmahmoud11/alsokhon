from itertools import groupby
from odoo.osv import expression
from odoo import api, fields, models , _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
from datetime import date, timedelta

class fixing_unfixed_bill(models.Model):
    _name = 'fixing.unfixed.bill'
    _description = 'Fixing Unfixed Bill'

    value = fields.Float()
    gold_rate = fields.Float()

    @api.onchange('value')
    def check_limit(self):
        if self.value:
            active_ids = self._context.get('active_ids') or self._context.get('active_id')
            account_move = self.env['account.move'].browse(active_ids)
            remaining_gold = account_move.pure_wt_value
            if self.value > remaining_gold:
                raise ValidationError(_('Wrong Value'))

    def process_fixing(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        account_move = self.env['account.move'].browse(active_ids)
        account_move.gold_rate_value = self.gold_rate
        account_move.convert_fixed(self.value)
