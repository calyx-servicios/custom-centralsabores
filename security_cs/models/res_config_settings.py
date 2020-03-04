# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    company_share_analytic = fields.Boolean(string='Share analytics to all companies',
        help="Share your analytics to all companies defined in your instance.\n"
             " * Checked : analytics are visible for every companies, even if a company is defined on the analytic.\n"
             " * Unchecked : Each company can see only its analytic (analytics where company is defined). analytics not related to a company are visible for all companies.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            company_share_analytic=not self.env.ref('analytic.analytic_comp_rule').active,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.ref('analytic.analytic_comp_rule').write({'active': not self.company_share_analytic})