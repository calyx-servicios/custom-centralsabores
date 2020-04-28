# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re

from odoo import http, _, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
)
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request, content_disposition
from odoo.tools import consteq
from odoo.addons.account.controllers.portal import PortalAccount


class PortalEasy(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(PortalEasy, self)._prepare_portal_layout_values()
        partner = request.env["res.users"].browse(request.uid).partner_id
        invoice_count = (
            request.env["easy.invoice"]
            .sudo()
            .search_count(
                [
                    ("state", "in", ("open", "paid")),
                    ("partner_id", "=", partner.id),
                ]
            )
        )
        easy_partner_count = (
            request.env["easy.partner.cc"]
            .sudo()
            .search_count([("partner_id", "=", partner.id)])
        )
        partner_balance = (
            request.env["res.partner"]
            .sudo()
            .search_read([("id", "=", partner.id)], limit=1)
        )
        values["easy_invoice_count"] = invoice_count
        values["easy_partner_count"] = easy_partner_count
        values["easy_amount_balance"] = partner_balance[0][
            "easy_amount_balance"
        ]
        values["odoo_amount_balance"] = partner_balance[0]["amount_balance"]
        values["total_easy_amount_balance"] = partner_balance[0][
            "total_amount_balance"
        ]
        return values

    def _document_check_easy_access(self, model_name, document_id, partner):
        document = request.env[model_name].sudo().browse([document_id])
        document_sudo = False
        # document_sudo = document.with_user(SUPERUSER_ID).exists()
        if document.partner_id == partner:
            document_sudo = True
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        return document

    def _invoice_get_page_view_values_easy(
        self, invoice, access_token, **kwargs
    ):
        values = {
            "page_name": "easy invoice",
            "invoice": invoice,
        }
        return self._get_page_view_values(
            invoice,
            access_token,
            values,
            "my_invoices_history",
            False,
            **kwargs
        )

    ####################################
    # #######   EASY INVOICE   #########
    ####################################

    @http.route(
        ["/my/easy_invoices", "/my/easy_invoices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_easy_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = {}
        partner = request.env["res.users"].browse(request.uid).partner_id
        items_per_page = 10
        AccountInvoice = request.env["easy.invoice"]

        domain = [
            ("state", "in", ("open", "paid")),
            ("partner_id", "=", partner.id),
        ]

        searchbar_sortings = {
            "date": {"label": _("Invoice Date"), "order": "date_invoice desc"},
            "duedate": {
                "label": _("Due Date"),
                "order": "date_expiration desc",
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
        invoice_count = AccountInvoice.sudo().search_count(domain)
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
            step=items_per_page,
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.sudo().search(
            domain, order=order, limit=items_per_page, offset=pager["offset"],
        )
        request.session["my_invoices_history"] = invoices.ids[:100]

        easy_invoices_total = 0
        for invoice in invoices:
            easy_invoices_total += invoice.residual_amount

        values.update(
            {
                "date": date_begin,
                "invoices": invoices,
                "easy_invoices_total": easy_invoices_total,
                "page_name": "easy invoice",
                "pager": pager,
                "default_url": "/my/invoices",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("easy_web.portal_my_easy_invoices", values)

    @http.route(
        ["/my/easy_invoices/<int:easy_invoice_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_easy_invoice_detail(
        self,
        easy_invoice_id,
        access_token=None,
        report_type=None,
        download=False,
        **kw
    ):

        partner = request.env["res.users"].browse(request.uid).partner_id

        try:
            invoice_sudo = self._document_check_easy_access(
                "easy.invoice", easy_invoice_id, partner
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=invoice_sudo,
                report_type=report_type,
                report_ref="account.account_invoices",
                download=download,
            )

        values = {
            "page_name": "easy invoice",
            "invoice": invoice_sudo,
        }
        # values = self._invoice_get_page_view_values(
        #     invoice_sudo, access_token, **kw
        # )
        # acquirers = values.get("acquirers")
        # if acquirers:
        #     country_id = (
        #         values.get("partner_id")
        #         and values.get("partner_id")[0].country_id.id
        #     )
        #     values["acq_extra_fees"] = acquirers.get_acquirer_extra_fees(
        #         invoice_sudo.amount_residual,
        #         invoice_sudo.currency_id,
        #         country_id,
        #     )

        return request.render(
            "easy_web.portal_easy_invoice_page_detail", values
        )

    ####################################
    # ###### EASY INVOICE REPORT #######
    ####################################

    @http.route(
        ["/my/easy_invoices/pdf/<int:easy_invoice_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_easy_invoice_report(
        self, easy_invoice_id, access_token=None, **kw
    ):

        partner = request.env["res.users"].browse(request.uid).partner_id
        try:
            invoice_sudo = self._document_check_easy_access(
                "easy.invoice", easy_invoice_id, partner
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        return self._show_report(
            model=invoice_sudo,
            report_type="pdf",
            report_ref="easy_invoice.action_report_easyinvoice",
            download=True,
        )

    ####################################
    # #######   EASY PARTNER   #########
    ####################################

    @http.route(
        ["/my/easy_partner", "/my/easy_partner/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_easy_invoices_partner(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = {}
        partner = request.env["res.users"].browse(request.uid).partner_id
        items_per_page = 10
        easy_invoice_partner = request.env["easy.partner.cc"]

        domain = [("partner_id", "=", partner.id)]

        searchbar_sortings = {
            "date": {"label": _("Invoice Date"), "order": "date desc"},
            "description": {
                "label": _("Reference"),
                "order": "description desc",
            },
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
        invoice_count = easy_invoice_partner.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/easy_partner",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=invoice_count,
            page=page,
            step=items_per_page,
        )
        # content according to pager and archive selected
        receipts = easy_invoice_partner.sudo().search(
            domain, order=order, limit=items_per_page, offset=pager["offset"],
        )
        receipt_total = 0
        receipt_advancement = 0

        for receipt in receipts:
            receipt_total += receipt.amount_anticipe
            receipt_advancement += receipt.amount_advancement

        request.session["my_invoices_history"] = receipts.ids[:100]

        values.update(
            {
                "date": date_begin,
                "receipts": receipts,
                "receipt_total": receipt_total,
                "receipt_advancement": receipt_advancement,
                "page_name": "easy partner",
                "pager": pager,
                "default_url": "/my/easy_partner",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render(
            "easy_web.portal_my_easy_invoice_partner", values
        )

    ####################################
    # #######   INVOICE   #########
    ####################################
    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ("html", "pdf", "text"):
            raise UserError(_("Invalid report type: %s") % report_type)

        report_sudo = request.env.ref(report_ref).sudo()

        if not isinstance(report_sudo, type(request.env["ir.actions.report"])):
            raise UserError(
                _("%s is not the reference of a report") % report_ref
            )

        method_name = "render_qweb_%s" % (report_type)
        report = getattr(report_sudo, method_name)(
            [model.id], data={"report_type": report_type}
        )[0]
        reporthttpheaders = [
            (
                "Content-Type",
                "application/pdf" if report_type == "pdf" else "text/html",
            ),
            ("Content-Length", len(report)),
        ]
        if report_type == "pdf" and download:
            filename = "%s.pdf" % (
                re.sub("\W+", "-", model._get_report_base_filename())
            )
            reporthttpheaders.append(
                ("Content-Disposition", content_disposition(filename))
            )
        return request.make_response(report, headers=reporthttpheaders)
