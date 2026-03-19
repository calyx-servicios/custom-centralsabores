# -*- coding: utf-8 -*-
{
    "name": "Central Sabores Stock Fix",
    "summary": "Accion para suprimir pickings con borrado forzado.",
    "author": "Calyx Servicios S.A.",
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Inventory",
    "version": "11.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "reusable_sql_fetch_and_delete",
    ],
    "data": [
        "views/stock_picking_actions.xml",
    ],
}
