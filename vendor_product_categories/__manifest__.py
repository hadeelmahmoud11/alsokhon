# -*- coding: utf-8 -*-
{
    'name': 'Vendor Product Categories',
    'version': '13.0',
    'category': 'Purchase',
    'website': '',
    'summary': '',
    'description': """
        Add new fields in res partner and purchase order to relate vendors with the product categories they sell
    URLs:
    ====
    https://system.white-code.co.uk/web#id=989&action=395&model=project.task&view_type=form&menu_id=
    """,
    'depends': [
        'base', 'purchase'
    ],
    'data': [
        'views/vendor_product_categories_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
