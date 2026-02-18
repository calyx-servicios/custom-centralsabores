# -*- coding: utf-8 -*-
{
    'name': 'Purchase Scheduler Block',
    'summary': """
        Bloquea la generación de nuevas PO desde el scheduler y valida productos pendientes""",

    'author': 'Calyx Servicios S.A.',
    'website': 'https://odoo.calyx-cloud.com.ar/',
    'license': 'AGPL-3',

    'category': 'Purchase',
    'version': '11.0.1.0.0',
    'development_status': 'Production/Stable',

    'application': False,
    'installable': True,

    'depends': ['base', 'purchase', 'stock'],

    'data': [
        'data/ir_config_parameter_data.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
}

