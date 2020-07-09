# -*- coding: utf-8 -*-
{
    'name': "Gold Rate",
    'description': """
       Gold Rate""",
    'author': "White-Code, Kalpesh Gajera",
    'website': "http://www.white-code.co.uk",
    'URL': "https://system.white-code.co.uk/web?#id=1668&action=395&model=project.task&view_type=form&menu_id=263",
    'category': 'Account',
    'version': '13.0.0.1',
    'depends': ['account', 'currency_rate_live'],
    'data': [
        'security/ir.model.access.csv',
        'data/currency_data.xml',
        'views/gold_rate_view.xml',
        'views/res_currency_view.xml',
    ],

}
