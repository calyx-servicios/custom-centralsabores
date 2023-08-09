# -*- coding: utf-8 -*-
{
    'name': "Product Pricelist Permision Custom",
    'summary': """
        Permisos especiales para la gestion de listas de precios en productos de Central Sabores""",

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Customs',
    'version': '11.0.0.0.0',
    'depends' : ['sale',
                 'price_security',
        ],
    'data': [
        'security/sale_security.xml',
        'views/product_view.xml'
    ],
}