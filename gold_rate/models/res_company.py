# -*- coding: utf-8 -*-
import requests
from lxml import etree
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    def update_currency_rates(self):
        res = super(ResCompany, self).update_currency_rates()
        # Get Gold Rates
        rslt = True
        active_currencies = self.env['res.currency'].search([
            ('is_gold', '=', True)])
        for (currency_provider, companies) in self._group_by_provider().items():
            parse_results = None
            parse_function = getattr(companies,
                                     'get_gold_rate')
            parse_results = parse_function(active_currencies)
            if parse_results and parse_results == False:
                # We check == False, and don't use bool conversion, as an empty
                # dict can be returned, if none of the available currencies is supported by the provider
                _logger.warning(_(
                    'Unable to connect to the online exchange gold rate '
                    'platform %s. The web service may be temporary down.') % currency_provider)
                rslt = False
            else:
                companies._generate_gold_rates(parse_results)
        return res

    def get_gold_rate(self, available_currencies):
        """
            Gold rate always get based on currency XAU
        """
        url_format = 'http://www.xe.com/currencytables/?from=%(currency_code)s'
        today = fields.Date.today()

        # We generate all the exchange rates relative to the USD. This is purely arbitrary.
        try:
            fetched_data = requests.request('GET', url_format % {
                'currency_code': 'XAU'})
        except:
            return False

        rslt = {}
        available_currency_names = available_currencies.mapped('name')

        if 'XAU' in available_currency_names:
            rslt['XAU'] = (1.0, today)

        htmlelem = etree.fromstring(fetched_data.content, etree.HTMLParser())
        rates_table = htmlelem.find(".//table[@id='historicalRateTbl']/tbody")
        for rate_entry in list(rates_table):
            if type(
                    rate_entry) != etree._Comment:  # The returned HTML always contains commented lines (for some reason), so we ignore them
                currency_code = rate_entry.find('.//a').text
                if currency_code in available_currency_names:
                    rate = float(rate_entry.find(
                        "td[@class='historicalRateTable-rateHeader']["
                        "last()]").text)
                    rslt[currency_code] = (rate, today)
        return rslt

    def _generate_gold_rates(self, parsed_data):
        if not parsed_data:
            return True
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
                currency_object = Currency.search([
                    ('is_gold', '=', True), ('name', '=', currency)])
                already_existing_rate = GoldRate.search(
                    [('currency_id', '=', currency_object.id),
                     ('name', '=', date_rate), ('company_id', '=', company.id)])
                if already_existing_rate:
                    already_existing_rate.rate = rate
                elif currency_object:
                    GoldRate.create(
                        {'currency_id': currency_object.id, 'rate': rate,
                         'name': date_rate, 'company_id': company.id})
