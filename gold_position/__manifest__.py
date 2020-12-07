# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Gold Position Reports",
    'summary': "Gold Position Reports",
    'author': "Hashem Aly",
    'category': 'account',
    'version': '13.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'gold_capital',
        'gold_purchases',
        'account_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/gold_position.xml',
        'views/gold_position.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
