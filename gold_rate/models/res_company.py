# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Override : To create records for gold rates
    def _generate_currency_rates(self, parsed_data):
        """ Generate the currency rate entries for each of the companies, using the
        result of a parsing function, given as parameter, to get the rates data.

        This function ensures the currency rates of each company are computed,
        based on parsed_data, so that the currency of this company receives rate=1.
        This is done so because a lot of users find it convenient to have the
        exchange rate of their main currency equal to one in Odoo.
        """
        res = super(ResCompany, self)._generate_currency_rates(parsed_data)
        Currency = self.env['res.currency']
        GoldRate = self.env['gold.rates']
        today = fields.Date.today()
        for company in self:
            rate_info = parsed_data.get(company.currency_id.name, None)

            if not rate_info:
                raise UserError(_(
                    "Your main currency (%s) is not supported by this exchange rate provider. Please choose another one.") % company.currency_id.name)

            base_currency_rate = rate_info[0]

            for currency, (rate, date_rate) in parsed_data.items():
                rate_value = rate / base_currency_rate

                currency_object = Currency.search([
                    ('is_gold', '=', True), ('name', '=', currency)])
                already_existing_rate = GoldRate.search(
                    [('currency_id', '=', currency_object.id),
                     ('name', '=', date_rate), ('company_id', '=', company.id)])
                if already_existing_rate:
                    already_existing_rate.rate = rate_value
                elif currency_object:
                    GoldRate.create(
                        {'currency_id': currency_object.id, 'rate': rate_value,
                         'name': date_rate, 'company_id': company.id})
        return res
