# -*- coding: utf-8 -*-
{
    'name': 'Vendor Events History Details',
    'version': '13.0',
    'category': 'Uncategorized',
    'website': '',
    'summary': '',
    'description': """
        Add new fields in res partner and Calender events to record all event history on the vendor details
    URLs:
    ====
    https://system.white-code.co.uk/web#id=1002&action=395&model=project.task&view_type=form&menu_id=
    """,
    'depends': [
        'base', 'calendar'
    ],
    'data': [
        'views/vendor_events_history_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
