# -*- coding: utf-8 -*-
{
    'name': "Stock CMV",
    'summary': """
        Stock CMV custom report""",

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Customs',
    'version': '11.0.1.0.0',
    'depends' : [
        'base',
        'stock',
        'stock_account',
        ],
    'data': [
        'views/stock_account_views.xml',
        'views/products_view.xml',
    ],
}