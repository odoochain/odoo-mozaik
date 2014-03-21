# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.tools import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class test_partner_relation_category(SharedSetupTransactionCase):

    _data_files = ('data/relation_data.xml',
                  )

    _module_ns = 'ficep_person'

    def setUp(self):
        super(test_partner_relation_category, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        self.model_partner_relation_category = self.registry('partner.relation.category')

    def test_name_get(self):
        relation_id = self.ref("ficep_person.partner_relation")
        res = self.model_partner_relation_category.name_get(self.cr, SUPERUSER_ID, [relation_id], context=None)
        self.assertEqual('employs', res[0][1], "Without context: should be subject name")
        res = self.model_partner_relation_category.name_get(self.cr, SUPERUSER_ID, [relation_id], context={'object': False})
        self.assertEqual('employs', res[0][1], "Without object false into context: should be subject name")
        res = self.model_partner_relation_category.name_get(self.cr, SUPERUSER_ID, [relation_id], context={'object': True})
        self.assertEqual('is used by', res[0][1], "With object into context: should be object name")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
