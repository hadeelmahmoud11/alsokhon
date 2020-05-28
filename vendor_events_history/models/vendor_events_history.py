from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    events_count = fields.Integer(compute='compute_count')

    def compute_count(self):
        for record in self:
            record.events_count = self.env['calendar.event'].search_count(
                [('vendor_id', '=', self.id)])

    def get_calendar_events(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calendar Events',
            'view_mode': 'calendar,tree',
            'res_model': 'calendar.event',
            'domain': [('vendor_id', '=', self.id)],
            'context': "{'create': False}"
        }


class CalenderEvent(models.Model):
    _inherit = 'calendar.event'

    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor')
