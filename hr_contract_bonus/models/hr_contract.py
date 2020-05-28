from odoo import api,fields,models,_
from datetime import datetime, timedelta, time

class HRContract(models.Model):
    _inherit = 'hr.contract'

    bonus = fields.Float('Bonus')
