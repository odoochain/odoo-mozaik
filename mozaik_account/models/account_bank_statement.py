# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    @api.multi
    def auto_reconcile(self):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda l: not (not l.partner_id or l.journal_entry_ids)
        )
        if not lines:
            return False
        lines._auto_reconcile()
        return True
