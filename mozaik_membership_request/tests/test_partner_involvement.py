# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestInvolvement(TransactionCase):
    def test_involvment(self):
        """
        Check for creation of involvement when validating
        """
        # create an involvement category
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Les hommes viennent de Mars...",
                "code": "Mars",
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        # create a membership request
        mr = self.env["membership.request"].create(
            {
                "lastname": "Venus",
                "involvement_category_ids": [(6, 0, [cat.id])],
            }
        )
        # validate it
        mr.validate_request()
        partner = mr.partner_id
        # an involvement related to the choosen category is created
        self.assertEqual(cat, partner.partner_involvement_ids.involvement_category_id)
        # make another membership request
        mrid = partner.button_modification_request()["res_id"]
        mr = self.env["membership.request"].browse(mrid)
        # create an involvement category
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Les femmes viennent de Venus...",
                "code": "Venus",
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        # add it to the involvement categories
        mr.involvement_category_ids |= cat
        # validate the request
        mr.validate_request()
        # partner has now 2 involvements
        codes = partner.partner_involvement_ids.mapped("involvement_category_id.code")
        codes.sort()
        self.assertEqual(["Mars", "Venus"], codes)

    def test_multi_donation(self):
        """
        Check for multi donation payment data propagation when validating
        """
        # create an involvement category
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Protégons nos arrières...",
                "code": "PA",
                "involvement_type": "donation",
                "allow_multi": True,
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        # create a membership request
        now = fields.Datetime.to_string(datetime.now() + timedelta(hours=-1))
        mr = self.env["membership.request"].create(
            {
                "lastname": "Rocky",
                "involvement_category_ids": [(6, 0, [cat.id])],
                "amount": 8.5,
                "effective_time": now,
            }
        )
        # validate it
        mr.validate_request()
        partner = mr.partner_id
        # check for amount and reference on related donation involvement
        donation = partner.partner_involvement_ids.filtered(
            lambda s: s.involvement_category_id.code == "PA"
        )
        self.assertEqual(8.5, donation.amount)
        self.assertFalse(donation.reference)
        self.assertEqual(mr.effective_time, donation.effective_time)
        # create another membership request with a reference
        mr = self.env["membership.request"].create(
            {
                "lastname": "Rocky",
                "partner_id": partner.id,
                "involvement_category_ids": [(6, 0, [cat.id])],
                "amount": 9.0,
                "reference": "PA-2017-00023",
                "effective_time": fields.Datetime.now(),
            }
        )
        # validate it
        mr.validate_request()
        # check for amount and reference on related donation involvement
        donations = partner.partner_involvement_ids.filtered(
            lambda s: s.involvement_category_id.code == "PA"
        )
        self.assertEqual(2, len(donations))
        donation = donations.filtered(lambda s: s.amount == 9.0)
        self.assertEqual(mr.reference, donation.reference)
        self.assertEqual(mr.effective_time, donation.effective_time)
