# -*- coding: utf-8 -*-
{
    "name": "Easy Invoice Portal",
    "summary": """
        Custom Easy Invoice Portal""",
    "description": """
        
    """,
    "author": "Calyx",
    "website": "http://www.calyxservicios.com.ar",
    "category": "Customs",
    "version": "11.0.1.0.0",
    "depends": [
        "easy_invoice",
        "easy_invoice_partner_cc",
        "portal",
        "website",
        "account",
    ],
    "data": [
        # 'views/sale_views.xml',
        "views/easy_invoice_portal_template.xml",
        "views/easy_partner_portal_template.xml",
        "security/ir.model.access.csv",
    ],
}
