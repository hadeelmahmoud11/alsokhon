# -*- coding: utf-8 -*-
{
    'name': "Diamond Enhancements",
    'description': """
       Diamond Enhancements""",
    'author': "White-Code, Abdulrahman Warda",
    'website': "http://www.white-code.co.uk",
    'URL': "https://system.white-code.co.uk/web#id=1667&action=395&model=project.task&view_type=form&menu_id=263",
    'category': 'Sales',
    'version': '13.0.0.1',
    # 'depends': ['purchase_stock', 'stock_account','account','po_gold_form','purchase_product_matrix',
    #             'purchase_order_type', 'account_accountant','stock','account_reports'],
    'depends': ['gold_sales','gold_purchases','sale_stock', 'stock_account','account', 'account_accountant','stock','account_reports','sale_order_type','sale'],
    'data': [
        'views/views.xml',
    ],

}
