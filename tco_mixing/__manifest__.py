# -*- coding: utf-8 -*-
{
    'name': "Mixing - TUICO",
    'summary': """Mixing model""",
    'description': """Managing Mixing information""",
    'author': "tuicovn.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product', 'stock', 'portal', 'mail', 'utm',
    ],
    'data': [
        'security/tco_mixing_security.xml',
        'security/ir.model.access.csv',
        'views/tco_mixing.xml',
        'views/tco_mixing_gc.xml',
        'views/stock_picking.xml',

    ],

    # 'qweb': ['static/src/xml/*.xml'],
    'assets': {
        'web.assets_backend': [

        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
