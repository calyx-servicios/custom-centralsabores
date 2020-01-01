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
    'depends': ['base', 'contacts', 'l10n_ar_partner', 'easy_invoice', 'sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],

    'demo': [
    ],
}