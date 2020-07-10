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
