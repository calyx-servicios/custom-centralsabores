{
    'name': 'Easy Invoice Report Custom',
    'version': '11.0.1',
    'category': 'Tools',
    'author': "Calyx",
    'maintainers': ['DarwinAndrade'],
    'website': 'www.calyxservicios.com.ar',
    'license': 'AGPL-3',
    'summary': '''changes in the report I send''',
    'depends': [
        'stock', 'easy_invoice', 'sale'
    ],
    'external_dependencies': {
    },
    'data': [
        'reports/invoice_template.xml',
        'view/easy_invoice_view.xml',
        'view/sale_order_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
