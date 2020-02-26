# -*- coding: utf-8 -*-
{
    'name': "Sale Analytic",
    'summary': """
        Custom Sale Analytic Default for Products""",

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Customs',
    'version': '11.0.1.0.0',
    'depends' : [
        'base',
        'analytic',
        'sale',
        'easy_invoice',
        'easy_invoice_sale',
        'easy_invoice_analytic_relation',
        ],
    'data': [
        # 'views/sale_views.xml',
        'views/product_view.xml',
    ],
}