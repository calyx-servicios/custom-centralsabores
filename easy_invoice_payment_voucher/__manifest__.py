# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Paymnet Boucher",
    'summary': """
        Easy Invoice Payment Boucher""",

    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'base',
        'easy_invoice',
        'easy_invoice_recaudation'
        ],
    'data': [
        'report/payment_group_report.xml',
        'report/payment_group_template.xml',
    ],
}