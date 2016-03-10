# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import tempfile
import csv
import base64
from collections import OrderedDict

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp.addons.mozaik_person.res_partner import available_genders, \
    available_tongues
from export_csv_request import VIRTUAL_TARGET_REQUEST
from export_csv_request import EMAIL_COORDINATE_REQUEST
from export_csv_request import POSTAL_COORDINATE_REQUEST

HEADER_ROW = [
    'Internal Identifier',
    'Name',
    'Lastname',
    'Firstname',
    'Usual Lastname',
    'Usual Firstname',
    'Co-residency Line 1',
    'Co-residency Line 2',
    'Internal Instance',
    'Power Level',
    'Status',
    'Reference',
    'Birthdate',
    'Gender',
    'Tongue',
    'Main Address',
    'Unauthorized Address',
    'Vip Address',
    'Street2',
    'Street',
    'Zip',
    'City',
    'Country Code',
    'Country Name',
    'Main Phone',
    'Unauthorized Phone',
    'Vip Phone',
    'Phone',
    'Main Mobile',
    'Unauthorized Mobile',
    'Vip Mobile',
    'Mobile',
    'Main Fax',
    'Unauthorized Fax',
    'Vip Fax',
    'Fax',
    'Main Email',
    'Unauthorized Email',
    'Vip Email',
    'Email',
    'Website',
    'Secondary Website',
]


class export_csv(orm.TransientModel):
    _name = 'export.csv'
    _description = 'Export CSV Wizard'

    _columns = {
        'export_file': fields.binary('Vcf', readonly=True),
        'export_filename': fields.char('Export VCF Filename', size=128),
    }

    def get_csv_rows(self, cr, uid, model, context=None):
        """
        Get the rows (header) for the specified model.
        """
        return HEADER_ROW

    def _get_order_by(self, order_by):
        r_order_by = "ORDER BY p.id"
        if order_by:
            if order_by == "identifier" or order_by == "technical_name":
                r_order_by = "ORDER BY p.%s" % order_by
            else:
                r_order_by =\
                    "ORDER BY country_name, final_zip, p.technical_name"
        return r_order_by

    def get_csv_values(self, cr, uid, model, obj, context=None):
        """
        Get the values of the specified obj, which should be an instance
        of the specified model, either an email or a postal coordinate.
        """
        def _get_utf8(data):
            if not data:
                return None
            return unicode(data).encode('utf-8', 'ignore')

        export_values = OrderedDict([
            ('identifier', obj.get('identifier')),
            ('name', _get_utf8(obj.get('name'))),
            ('lastname', _get_utf8(obj.get('lastname'))),
            ('firstname', _get_utf8(obj.get('firstname'))),
            ('usual_lastname', _get_utf8(obj.get('usual_lastname'))),
            ('usual_firstname', _get_utf8(obj.get('usual_firstname'))),
            ('printable_name', _get_utf8(obj.get('printable_name'))),
            ('co_residency', _get_utf8(obj.get('co_residency'))),
            ('instance', _get_utf8(obj.get('instance'))),
            ('power_name', _get_utf8(obj.get('power_name'))),
            ('status', _get_utf8(obj.get('status'))),
            ('reference', _get_utf8(obj.get('reference'))),
            ('birth_date', obj.get('birth_date')),
            ('gender', available_genders.get(obj.get('gender'))),
            ('tongue', available_tongues.get(obj.get('tongue'))),
            ('adr_main', obj.get('adr_main')),
            ('adr_unauthorized', obj.get('adr_unauthorized')),
            ('adr_vip', obj.get('adr_vip')),
            ('street2', _get_utf8(obj.get('street2'))),
            ('street', _get_utf8(obj.get('street'))),
            ('zip', obj.get('final_zip')),
            ('city', _get_utf8(obj.get('city'))),
            ('country_code', obj.get('country_code')),
            ('country_name', _get_utf8(obj.get('country_name'))),
            ('fix_main', obj.get('fix_main')),
            ('fix_unauthorized', obj.get('fix_unauthorized')),
            ('fix_vip', obj.get('fix_vip')),
            ('fix', _get_utf8(obj.get('fix'))),
            ('mobile_main', obj.get('mobile_main')),
            ('mobile_unauthorized', obj.get('mobile_unauthorized')),
            ('mobile_vip', obj.get('mobile_vip')),
            ('mobile', _get_utf8(obj.get('mobile'))),
            ('fax_main', obj.get('fax_main')),
            ('fax_unauthorized', obj.get('fax_unauthorized')),
            ('fax_vip', obj.get('fax_vip')),
            ('fax', _get_utf8(obj.get('fax'))),
            ('email_main', obj.get('email_main')),
            ('email_unauthorized', obj.get('email_unauthorized')),
            ('email_vip', obj.get('email_vip')),
            ('email', _get_utf8(obj.get('email'))),
            ('website', _get_utf8(obj.get('website'))),
            ('secondary_website', _get_utf8(obj.get('secondary_website'))),
        ])
        return export_values

    def _prefetch_csv_datas(self, cr, uid, model, model_ids, context=None):
        if not model_ids:
            return
        if model == 'email.coordinate':
            query = """
            %s WHERE ec.id IN %%s
            """ % EMAIL_COORDINATE_REQUEST
        elif model == 'postal.coordinate':
            query = """
            %s WHERE pc.id IN %%s
            """ % POSTAL_COORDINATE_REQUEST
        elif model == 'virtual.target':
            query = """
            %s WHERE vt.id IN %%s
            """ % VIRTUAL_TARGET_REQUEST
        else:
            raise orm.except_orm(
                _('Error'),
                _('Model %s Not supported for csv generation!') % model)
        order_by = self._get_order_by(context.get('sort_by'))
        query = "%s %s" % (query, order_by)
        cr.execute(query, (tuple(model_ids),))
        for row in cr.dictfetchall():
            yield row

    def get_csv(self, cr, uid, model, model_ids, group_by=False, context=None):
        """
        Build a CSV file related to a coordinate model
        """
        tmp = tempfile.NamedTemporaryFile(
            prefix='Extract', suffix=".csv", delete=False)
        f = open(tmp.name, "r+")
        writer = csv.writer(f)
        writer.writerow(self.get_csv_rows(cr, uid, model, context=context))
        co_residencies = []
        if model_ids:
            for data in self._prefetch_csv_datas(
                    cr, uid, model, model_ids, context=context):
                if model == 'postal.coordinate':
                    # when grouping by co_residency, output only one row
                    # by co_residency
                    if group_by and data.get(
                            'co_residency_id') in co_residencies:
                        continue
                    co_residencies.append(data.get('co_residency_id'))
                export_values = self.get_csv_values(cr, uid, model, data)
                if not export_values:
                    continue
                writer.writerow(export_values.values())
        f.close()
        f = open(tmp.name, "r")
        csv_content = f.read()
        f.close()
        return csv_content

    def export(self, cr, uid, ids, context=None):
        model = context.get('active_model', False)
        model_ids = context.get('active_ids', False)
        csv_content = self.get_csv(cr, uid, model, model_ids, context=context)

        csv_content = base64.encodestring(csv_content)

        self.write(cr, uid, ids[0],
                   {'export_file': csv_content,
                    'export_filename': 'Extract.csv'},
                   context=context)

        return {
            'name': 'Export Csv',
            'type': 'ir.actions.act_window',
            'res_model': 'export.csv',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }
