# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models


class GoldCapital(models.Model):
    _name = 'gold.capital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Gold Capital'

    name = fields.Float('Capital')
    log_ids = fields.One2many('gold.capital.logs', 'capital_id', 'Logs')

    def write(self, vals):
        old_value = 0
        for rec in self:
            old_value = rec.name
        res = super(GoldCapital, self).write(vals)
        log_obj = self.env['gold.capital.logs']

        lang_id = self.env['res.lang'].sudo().search([
            ('code', '=', self.env.user.lang)])
        for rec in self:
            log = log_obj.create({
                'date': fields.Datetime.now(),
                'old_capital': old_value,
                'new_capital': rec.name,
                'capital_diff': rec.name - old_value,
                'capital_id': rec.id,
                'user_id': self.env.user.id,
            })
            content = '%s | %s | %s | %s' % (datetime.strftime(
                log.date,
                '%s %s' % (
                    lang_id.date_format, lang_id.time_format)
            ), log.new_capital, log.old_capital, log.capital_diff)
            rec.message_post(body=content)
        return res


class GoldCapitalLogs(models.Model):
    _name = 'gold.capital.logs'

    date = fields.Datetime('Date')
    new_capital = fields.Float('New Capital')
    old_capital = fields.Float('Old Capital')
    capital_diff = fields.Float('Capital Difference')
    user_id = fields.Many2one('res.users', string='User')
    capital_id = fields.Many2one('gold.capital', string='Capital')
