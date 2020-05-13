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
        "base",
        "contacts",
        "l10n_ar_partner",
        "l10n_ar_account",
        "easy_invoice",
        "easy_invoice_partner_cc",
        "portal",
        "website",
        "account",
    ],
    "data": [
        "views/easy_invoice_portal_template.xml",
        "views/easy_partner_portal_template.xml",
        "views/res_partner_view.xml",
        "security/ir.model.access.csv",
    ],
}
