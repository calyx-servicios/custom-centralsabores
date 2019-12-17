# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Sale Customization Central Sabores",
    'summary': """
        Extención de Relación entre Ventas con Easy Invoice para Customización de Central Sabores""",

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Customs',
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice',
        'easy_invoice_sale',
        'easy_invoice_sale_automatization',
        'easy_invoice_partner_cc',
        #'easy_invoice_cost_center_relation',
        'easy_invoice_analytic_relation',
        'sale',
        'sale_management',
        'base',
        ],
    'data': [
        'views/sale_order_view.xml',
        'views/easy_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
}