# -*- coding: utf-8 -*-
{
    'name': "Security CS",
    'summary': """
        Security CS""",
    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['base', 'contacts', 'l10n_ar_partner', 'easy_invoice', 'sale', 'easy_invoice_sale', 'sale_management',
        'stock','stock_account','hr','hr_expense'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/easy_invoice.xml',
    ],

    'demo': [
    ],
}
