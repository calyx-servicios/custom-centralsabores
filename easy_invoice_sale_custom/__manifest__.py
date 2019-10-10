# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Sale Customization Central Sabores",
    'summary': """
        Extención de Relación entre Ventas con Easy Invoice para Customización de Central Sabores""",

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice_sale',
        'easy_invoice_cost_center_relation',
        'sale',
        'sale_management',
        ],
    'data': [
        'views/sale_order_view.xml',
    ],
}