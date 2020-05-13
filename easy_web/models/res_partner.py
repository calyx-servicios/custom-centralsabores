# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    portal_responsable = fields.Boolean(
        string="Portal Responsable", default=False
    )

    portal_partners_ids = fields.One2many(
        "res.partner.portal_contacts",
        "partner_responsable_id",
        string="Portal Contact",
    )


class ResPartnerPortal(models.Model):
    _name = "res.partner.portal_contacts"

    partner_portal_id = fields.Many2one("res.partner", string="Partner Portal")
    partner_responsable_id = fields.Many2one(
        "res.partner", string="Responsable"
    )
