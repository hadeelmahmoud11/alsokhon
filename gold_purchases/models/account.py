# -*- coding: utf-8 -*-
from odoo.osv import expression
from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    gold = fields.Boolean('Gold')


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    gold = fields.Boolean('Gold Journal')


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _query_get(self, options, domain=None):
        domain = self._get_options_domain(options) + (domain or [])
        self.env['account.move.line'].check_access_rights('read')
        domain = expression.AND([domain, [('journal_id.gold', '=', False)]])
        query = self.env['account.move.line']._where_calc(domain)
        # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
        self.env['account.move.line']._apply_ir_rules(query)
        return query.get_sql()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    gross_wt = fields.Float('Gross Wt', digits=(16, 3))
    purity_id = fields.Many2one('gold.purity', 'Purity')
    pure_wt = fields.Float('Pure Wt', digits=(16, 3))
    purity_diff = fields.Float('Purity +/-', digits=(16, 3))
    total_pure_weight = fields.Float('Pure Weight', digits=(16, 3))
    make_rate = fields.Monetary('Make Rate/G', digits=(16, 3))
    make_value = fields.Monetary('Make Value', digits=(16, 3))
    gold_rate = fields.Float('Gold Rate/G', digits=(16, 3))
    gold_value = fields.Monetary('Gold Value', digits=(16, 3))


