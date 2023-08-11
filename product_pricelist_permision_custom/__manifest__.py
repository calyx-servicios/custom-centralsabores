# -*- coding: utf-8 -*-
{
    "name": "Product Pricelist Permision Custom",
    "summary": """
        Special permits for the management of price lists for Central Sabores products""",

    "description": """
        - Only users who have the permission will be able to modify the price lists in a product
        - It is not allowed to enter duplicate price lists in a product
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["gpperez"],
    "website": "http://www.calyxservicios.com.ar",
    "category": "Customs",
    "version": "11.0.0.0.0",
    "development_status": "Production/Stable",
    "depends" : ["sale",
                 "price_security",],
    "data": [
        "security/sale_security.xml",
        "views/product_view.xml"],
    "application": False,
    "installable": True,
}
