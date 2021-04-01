# -*- coding: utf-8 -*-
{
    "name": "Easy Invoice Portal",
    "summary": """
        Custom Easy Invoice Portal""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["JhoneM"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "category": "Web",
    "version": "11.0.1.0.1",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "contacts",
        "l10n_ar_partner",
        "l10n_ar_account",
        "easy_invoice",
        "easy_invoice_partner_cc",
        "portal",
        "website",
        "account",
        "helpdesk_mgmt",
    ],
    "data": [
        "views/easy_invoice_portal_template.xml",
        "views/easy_partner_portal_template.xml",
        "views/res_partner_view.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
    ],
}
