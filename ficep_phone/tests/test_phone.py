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
from openerp.osv import orm
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_phone(common.TransactionCase):

    def setUp(self):
        super(test_phone, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_insert_without_prefix(self):
        num = self.registry('phone.phone')._check_and_format_number('061140220')
        self.assertEquals(num, '+32 61 14 02 20', '061140220 should give +32 61 14 02 20')

    def test_insert_with_prefix(self):
        num = self.registry('phone.phone')._check_and_format_number('+32489587520')
        self.assertEquals(num, '+32 489 58 75 20', '+32489587520 should give +32 489 58 75 20')

    def test_proper_escaping(self):
        num = self.registry('phone.phone')._check_and_format_number('061-54/10    45')
        self.assertEquals(num, '+32 61 54 10 45', '061-54/10    45 should give +32 61 54 10 45')

    def test_insert_bad_query(self):
        cr, uid = self.cr, self.uid
        self.assertRaises(orm.except_orm, self.registry('phone.phone')._check_and_format_number, cr, uid, 'badquery')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
