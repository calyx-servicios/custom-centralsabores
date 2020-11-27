from odoo import fields, models, _
from odoo.exceptions import Warning


class EasyCNTypes(models.Model):
    _name = "easy.invoice.cn.types"
    _rec_name = "cn_types"
    _order = "sequence"

    cn_types = fields.Char("CN Types")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    def unlink(self):
        sale_obj = self.env["easy.invoice"]
        rule_ranges = sale_obj.search([("cn_types_id", "=", self.id)])
        if rule_ranges:
            raise Warning(
                _(
                    "You are trying to delete a record "
                    "that is still referenced in one o more invoice, "
                    "try to archive it."
                )
            )
        return super(EasyCNTypes, self).unlink()
