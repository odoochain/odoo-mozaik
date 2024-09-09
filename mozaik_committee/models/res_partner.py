# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    sta_candidature_ids = fields.One2many(
        comodel_name="sta.candidature",
        inverse_name="partner_id",
        string="State Candidatures",
        domain=[("active", "=", True)],
    )
    sta_candidature_inactive_ids = fields.One2many(
        comodel_name="sta.candidature",
        inverse_name="partner_id",
        string="State Candidatures (Inactive)",
        domain=[("active", "=", False)],
    )
    int_candidature_ids = fields.One2many(
        comodel_name="int.candidature",
        inverse_name="partner_id",
        string="Internal Candidatures",
        domain=[("active", "=", True)],
    )
    int_candidature_inactive_ids = fields.One2many(
        comodel_name="int.candidature",
        inverse_name="partner_id",
        string="Internal Candidatures (Inactive)",
        domain=[("active", "=", False)],
    )
    ext_candidature_ids = fields.One2many(
        comodel_name="ext.candidature",
        inverse_name="partner_id",
        string="External Candidatures",
        domain=[("active", "=", True)],
    )
    ext_candidature_inactive_ids = fields.One2many(
        comodel_name="ext.candidature",
        inverse_name="partner_id",
        string="External Candidatures (Inactive)",
        domain=[("active", "=", False)],
    )

    def all_candidatures_action(self):
        self.ensure_one()
        context = {
            "search_default_partner_id": self.id,
            "default_partner_id": self.id,
            "search_default_all": True,
        }
        names = {
            "sta.candidature": _("State Candidatures"),
            "int.candidature": _("Internal Candidatures"),
            "ext.candidature": _("External Candidatures"),
        }
        candidature_model = self.env.context.get("candidature_model")
        return {
            "type": "ir.actions.act_window",
            "name": names[candidature_model],
            "res_model": candidature_model,
            "context": context,
            "view_mode": "tree,form",
        }
