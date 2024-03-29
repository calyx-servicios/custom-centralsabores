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
    'version': '11.0.2.1.0',
    'depends' : [
        'easy_invoice',
        'easy_invoice_sale',
        'security_cs',
        'easy_invoice_partner_cc',
        #'easy_invoice_cost_center_relation',
        'easy_invoice_analytic_relation',
        'sale',
        'sale_management',
        'sale_stock',
        'account_analytic_sale_in_line',
        'base',
        ],
    'data': [
        'views/sale_order_view.xml',
        "report/invoice_template.xml",
        #'views/easy_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/easy_payment_group_view.xml',
        'views/account_invoice_view.xml',
        'views/easy_invoice_view.xml',
    ],
}
