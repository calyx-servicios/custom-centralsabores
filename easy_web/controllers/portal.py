# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
)
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class PortalEasyAccount(CustomerPortal):

    # def _prepare_portal_layout_values(self):
    #     values = super(PortalEasyAccount, self)._prepare_portal_layout_values()
    #     invoice_count = request.env['account.move'].search_count([
    #         ('type', 'in', ('out_invoice', 'in_invoice', 'out_refund', 'in_refund', 'out_receipt', 'in_receipt')),
    #     ])
    #     values['invoice_count'] = invoice_count
    #     return values

    @http.route(
        ["/my/easy_invoices", "/my/easy_invoices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env["easy.invoice"]

        domain = [
            (
                "type",
                "in",
                (
                    "out_invoice",
                    "out_refund",
                    "in_invoice",
                    "in_refund",
                    "out_receipt",
                    "in_receipt",
                ),
            )
        ]

        searchbar_sortings = {
            "date": {"label": _("Invoice Date"), "order": "invoice_date desc"},
            "duedate": {
                "label": _("Due Date"),
                "order": "invoice_date_due desc",
            },
            "name": {"label": _("Reference"), "order": "name desc"},
            "state": {"label": _("Status"), "order": "state"},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # archive_groups = self._get_archive_groups('account.move', domain)
        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/easy_invoices",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=invoice_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        request.session["my_invoices_history"] = invoices.ids[:100]

        values.update(
            {
                "date": date_begin,
                "invoices": invoices,
                "page_name": "invoice",
                "pager": pager,
                #'archive_groups': archive_groups,
                "default_url": "/my/invoices",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("easy_web.portal_my_easy_invoices", values)
