# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
from odoo import http, _
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
)
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request, content_disposition
from odoo.osv.expression import OR
from collections import OrderedDict


class PortalEasy(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(PortalEasy, self)._prepare_portal_layout_values()
        partner = request.env["res.users"].browse(request.uid).partner_id
        partners = []

        for contacts in partner.portal_partners_ids:
            partners.append(contacts.partner_portal_id.id)

        partners.append(partner.id)

        invoice_count = (
            request.env["easy.invoice"]
            .sudo()
            .search_count(
                [
                    ("state", "in", ("open", "paid")),
                    ("partner_id", "in", partners),
                ]
            )
        )
        easy_partner_count = (
            request.env["easy.partner.cc"]
            .sudo()
            .search_count([("partner_id", "in", partners)])
        )
        partner_balance = (
            request.env["res.partner"].sudo().search([("id", "in", partners)])
        )
        easy_amount_balance = 0
        odoo_amount_balance = 0
        total_easy_amount_balance = 0

        for partner in partner_balance:
            easy_amount_balance += partner.easy_amount_balance
            odoo_amount_balance += partner.amount_balance
            total_easy_amount_balance += partner.total_amount_balance

        values["easy_invoice_count"] = invoice_count
        values["easy_partner_count"] = easy_partner_count
        values["easy_amount_balance"] = easy_amount_balance
        values["odoo_amount_balance"] = odoo_amount_balance
        values["total_easy_amount_balance"] = total_easy_amount_balance

        portal_responsable = False

        if partner.portal_responsable:
            portal_responsable = True

        values["partner_balance"] = partner_balance
        values["portal_responsable"] = portal_responsable

        return values

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
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        search=None,
        filterby=None,
        search_in="content",
        **kw
    ):
        values = {}
        partner = request.env["res.users"].browse(request.uid).partner_id

        partners = []

        for contacts in partner.portal_partners_ids:
            partners.append(contacts.partner_portal_id.id)

        partners.append(partner.id)

        items_per_page = 10
        AccountInvoice = request.env["easy.invoice"]

        domain = [
            ("state", "in", ("open", "paid")),
            ("partner_id", "in", partners),
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

        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
            "nc": {
                "label": _("Notas de Credito"),
                "domain": [("type", "=", "out_refund")],
            },
            "invoice": {
                "label": _("Facturas"),
                "domain": [("type", "=", "out_invoice")],
            },
        }

        searchbar_inputs = {
            "invoice": {
                "input": "invoice",
                "label": _(
                    "<span class='nolabel'>Buscar  </span>(en Facturas)"
                ),
            },
            "customer": {
                "input": "customer",
                "label": _("Search in Customer"),
            },
            "product": {
                "input": "product",
                "label": _(
                    "<span class='nolabel'>Buscar con </span>Productos"
                ),
            },
            "all": {"input": "all", "label": _("Search in All")},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        archive_groups = self._get_archive_groups("easy.invoice", domain)

        if date_begin:
            domain += [("create_date", ">", date_begin)]
        if date_end:
            domain += [("create_date", "<=", date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ("invoice", "all"):
                search_domain = OR(
                    [search_domain, [("name", "ilike", search)]]
                )
            if search_in in ("customer", "all"):
                search_domain = OR(
                    [search_domain, [("partner_id.name", "ilike", search)]]
                )
            if search_in == "product":
                search_domain = [
                    ("invoice_line_ids.product_id.name", "ilike", search)
                ]

            domain += search_domain

        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        invoice_count = AccountInvoice.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/easy_invoices",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
                "search_in": search_in,
                "search": search,
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
            easy_invoices_total += invoice.amount_total

        portal_responsable = False
        if partner.portal_responsable:
            portal_responsable = True

        values.update(
            {
                "date": date_begin,
                "date_end": date_end,
                "date": date_begin,
                "invoices": invoices,
                "archive_groups": archive_groups,
                "portal_responsable": portal_responsable,
                "easy_invoices_total": easy_invoices_total,
                "page_name": "easy invoice",
                "pager": pager,
                "default_url": "/my/easy_invoices",
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                # "searchbar_sortings": searchbar_sortings,
                # "searchbar_groupby": searchbar_groupby,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(
                    sorted(searchbar_filters.items())
                ),
                "filterby": filterby,
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
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        search=None,
        filterby=None,
        search_in="content",
        **kw
    ):
        values = {}
        partner = request.env["res.users"].browse(request.uid).partner_id
        partners = []

        for contacts in partner.portal_partners_ids:
            partners.append(contacts.partner_portal_id.id)

        partners.append(partner.id)

        items_per_page = 10
        easy_invoice_partner = request.env["easy.partner.cc"]

        domain = [("partner_id", "in", partners)]

        searchbar_sortings = {
            "date": {"label": _("Invoice Date"), "order": "date desc"},
            "description": {
                "label": _("Reference"),
                "order": "description desc",
            },
        }

        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
            "adv": {
                "label": _("Adelantos"),
                "domain": [("amount_advancement", ">", "0")],
            },
            "recp": {
                "label": _("Recibos"),
                "domain": [("amount_anticipe", ">", 0)],
            },
        }

        searchbar_inputs = {
            "description": {
                "input": "description",
                "label": _(
                    "Buscar <span class='nolabel'> (en Referencia) </span>"
                ),
            },
            "customer": {
                "input": "customer",
                "label": _("Search in Customer"),
            },
            "all": {"input": "all", "label": _("Search in All")},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]
        # SEARCH

        # search
        if search and search_in:
            search_domain = []
            if search_in in ("description", "all"):
                search_domain = OR(
                    [search_domain, [("description", "ilike", search)]]
                )
            if search_in in ("customer", "all"):
                search_domain = OR(
                    [search_domain, [("partner_id.name", "ilike", search)]]
                )
            domain += search_domain

        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]
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
                "filterby": filterby,
                "search_in": search_in,
                "search": search,
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

        portal_responsable = False

        if partner.portal_responsable:
            portal_responsable = True

        values.update(
            {
                "date": date_begin,
                "receipts": receipts,
                "searchbar_inputs": searchbar_inputs,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
                "portal_responsable": portal_responsable,
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
    # #######   FUNCTIONS   #########
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

    def _document_check_easy_access(self, model_name, document_id, partner):
        document = request.env[model_name].sudo().browse([document_id])
        document_sudo = False
        partners = []

        for contacts in partner.portal_partners_ids:
            partners.append(contacts.partner_portal_id.id)
        partners.append(partner.id)

        if document.partner_id.id in partners:
            document_sudo = True
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        return document
