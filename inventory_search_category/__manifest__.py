# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Inventory search for category',
    'summary': """
        This module allows you to perform internal category searches in the 
        stock movement lines and also by month and year period.""",

    'author': 'Calyx Servicios S.A., Odoo Community Association (OCA)',
    'maintainers': ['miltonguzmanf@gmail.com'],

    'website': 'http://odoo.calyx-cloud.com.ar/',
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '11.0.1.0.0',
    # see https://odoo-community.org/page/development-status
    'development_status': 'Production/Stable',

    'application': False,
    'installable': True,

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    'data': [
        'views/inventory_custom_search.xml',
    ],
}
