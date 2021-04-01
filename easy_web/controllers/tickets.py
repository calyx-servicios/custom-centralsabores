# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):
    @http.route(
        ["/my/tickets", "/my/tickets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tickets(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="all",
        **kw
    ):
        values = self._prepare_portal_layout_values()
        HelpdesTicket = request.env["helpdesk.ticket"]
        partner = request.env.user.partner_id

        team_ids = []
        ticket_team = (
            request.env["helpdesk.ticket.team"]
            .sudo()
            .search([("user_ids.partner_id", "in", partner.ids)])
        )

        for record in ticket_team:
            team_ids.append(record.id)

        domain = [
            "|",
            ("partner_id", "child_of", partner.id),
            ("team_id", "in", team_ids),
        ]

        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
            "update": {
                "label": _("Last Stage Update"),
                "order": "last_stage_update desc",
            },
        }

        # search input (text)
        searchbar_inputs = {
            "name": {"input": "name", "label": _("Search in Names")},
            "description": {
                "input": "description",
                "label": _("Search in Descriptions"),
            },
            "user_id": {
                "input": "user",
                "label": _("Search in Assigned users"),
            },
            "category_id": {
                "input": "category",
                "label": _("Search in Categories"),
            },
        }
        if self._message_content_field_exists():
            searchbar_inputs["message_content"] = {
                "input": "message_content",
                "label": _("Search in Messages"),
            }
        searchbar_meta_inputs = {
            "content": {
                "input": "content",
                "label": _("Search in Content"),
            },
            "all": {"input": "all", "label": _("Search in All")},
        }

        if search and search_in:
            search_domain = []
            if search_in == "content":
                search_domain = [
                    "|",
                    ("name", "ilike", search),
                    ("description", "ilike", search),
                ]

                if "message_content" in searchbar_inputs:
                    search_domain = OR(
                        [
                            search_domain,
                            [("message_content", "ilike", search)],
                        ]
                    )
            else:
                for search_property in [
                    k
                    for (k, v) in searchbar_inputs.items()
                    if search_in in (v["input"], "all")
                ]:
                    search_domain = OR(
                        [
                            search_domain,
                            [(search_property, "ilike", search)],
                        ]
                    )
            domain += search_domain
        searchbar_inputs.update(searchbar_meta_inputs)

        # search filters (by stage)
        searchbar_filters = {"all": {"label": _("All"), "domain": []}}
        for stage in request.env["helpdesk.ticket.stage"].search([]):
            searchbar_filters.update(
                {
                    str(stage.id): {
                        "label": stage.name,
                        "domain": [("stage_id", "=", stage.id)],
                    }
                }
            )

        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        ticket_count = HelpdesTicket.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={},
            total=ticket_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        tickets = HelpdesTicket.sudo().search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        values.update(
            {
                "date": date_begin,
                "tickets": tickets,
                "page_name": "ticket",
                "pager": pager,
                "default_url": "/my/tickets",
                "searchbar_sortings": searchbar_sortings,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "sortby": sortby,
                "no_breadcrumbs": False,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
            }
        )
        return request.render("helpdesk_mgmt.portal_my_tickets", values)
