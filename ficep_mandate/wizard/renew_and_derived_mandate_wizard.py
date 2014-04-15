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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.ficep_mandate import sta_mandate

WIZARD_AVAILABLE_ACTIONS = [
    ('renew', 'Renew mandate'),
    ('derived', 'Create derived mandate'),
]


class renew_and_derived_mandate_wizard(orm.TransientModel):
    _name = "renew.and.derived.mandate.wizard"

    _columns = {
        'sta_mandate_id': fields.many2one('sta.mandate', string='State mandate', readonly=True),
        'action': fields.selection(WIZARD_AVAILABLE_ACTIONS, 'Action'),
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category'),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'sta_assembly_id': fields.many2one('sta.assembly', string='State Assembly', readonly=True),
        'legislature_id': fields.many2one('legislature', string='Legislature'),
        'start_date': fields.date('Start Date'),
        'deadline_date': fields.date('Deadline Date'),
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = {}
        context = context or {}
        action = context.get('action', False)

        if not action:
            action = "renew"

        ids = context.get('active_id') and [context.get('active_id')] or context.get('active_ids') or []
        model = context.get('active_model', False)
        if not model:
            return res

        for mandate in self.pool[model].browse(cr, uid, ids, context=context):
            res['partner_id'] = mandate.partner_id.id
            res['mandate_category_id'] = mandate.mandate_category_id.id

            if isinstance(mandate._model, sta_mandate.sta_mandate):
                legislature_ids = self.pool['legislature'].search(cr, uid, [('power_level_id', '=', mandate.sta_assembly_id.assembly_category_id.power_level_id.id),
                                                                            ('start_date', '>', fields.datetime.now())])
                legislature_id = False
                if legislature_ids:
                    legislature_id = legislature_ids[0]

                res['legislature_id'] = legislature_id
                res['sta_assembly_id'] = mandate.sta_assembly_id.id
                res['sta_mandate_id'] = mandate.id

            break

        return res

    def onchange_legislature_id(self, cr, uid, ids, legislature_id, context=None):
        res = {}
        res['value'] = dict(mandate_start_date=False,
                                mandate_deadline_date=False)
        if legislature_id:
            legislature_data = self.pool.get('legislature').read(cr, uid, legislature_id, ['start_date', 'deadline_date'])
            res['value'] = dict(start_date=legislature_data['start_date'],
                                deadline_date=legislature_data['deadline_date'])
        return res

    def renew_mandate(self, cr, uid, ids, context=None):
        """
        ====================
        renew_mandate
        ====================
        Renew a mandate
        """
        if context.get('action', False) != 'renew':
            raise orm.except_orm(_('Error'), _('Action not allowed!'))

        wizard = self.browse(cr, uid, ids, context=context)[0]
        mandate_obj = self.pool[context.get('active_model')]

        res = dict(type='ir.actions.act_window',
                   view_type='form',
                   view_mode='form',
                   target='current',
                   nodestroy=True,
                   res_model=context.get('active_model'),
                   name=_(mandate_obj._description),)

        new_mandate_id = False
        view_id = False
        if isinstance(mandate_obj, sta_mandate.sta_mandate):
            values = dict(legislature_id=wizard.legislature_id.id,
                          start_date=wizard.start_date,
                          deadline_date=wizard.deadline_date)
            new_mandate_id = mandate_obj.copy(cr, uid, wizard.sta_mandate_id.id, default=values, context=context)
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_mandate', 'sta_mandate_form_view')
            view_id = view_ref and view_ref[1] or False,

        res['res_id'] = new_mandate_id
        res['view_id'] = view_id

        return res

    def create_derived_mandate(self, cr, uid, ids, context=None):
        """
        ====================
        create_derived_mandate
        ====================
        Create a derived mandate
        """
        if context.get('action', False) != 'derived':
            raise orm.except_orm(_('Error'), _('Action not allowed!'))

        wizard = self.browse(cr, uid, ids, context=context)[0]
        mandate_obj = self.pool[context.get('active_model')]

        res = dict(type='ir.actions.act_window',
                   view_type='form',
                   view_mode='form',
                   target='current',
                   nodestroy=True,
                   res_model=context.get('active_model'),
                   name=_(mandate_obj._description),)

        new_mandate_id = False
        view_id = False
        if isinstance(mandate_obj, sta_mandate.sta_mandate):
            values = dict(mandate_category_id=wizard.mandate_category_id.id,
                          start_date=wizard.start_date,
                          deadline_date=wizard.deadline_date)
            new_mandate_id = mandate_obj.copy(cr, uid, wizard.sta_mandate_id.id, default=values, context=context)
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_mandate', 'sta_mandate_form_view')
            view_id = view_ref and view_ref[1] or False,

        res['res_id'] = new_mandate_id
        res['view_id'] = view_id

        return res
