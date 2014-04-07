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
from openerp.tools import SUPERUSER_ID

from openerp.addons.base.res import res_partner


# Constants
AVAILABLE_GENDERS = [
                     ('m', 'Male'),
                     ('f', 'Female'),
                    ]

available_genders = dict(AVAILABLE_GENDERS)

AVAILABLE_CIVIL_STATUS = [
                          ('u', 'Unmarried'),
                          ('m', 'Married'),
                          ('d', 'Divorced'),
                         ]

available_civil_status = dict(AVAILABLE_CIVIL_STATUS)

AVAILABLE_TONGUES = [
                     ('f', 'French'),
                     ('g', 'German'),
                    ]

available_tongues = dict(AVAILABLE_TONGUES)


class res_partner(orm.Model):

    _name = 'res.partner'
    _inherit = ['mail.thread', 'res.partner', 'abstract.duplicate']

    _discriminant_field = 'name'
    _trigger_fileds = ['name', 'lastname', 'firstname', 'birth_date']
    _undo_redirect_action = 'ficep_person.all_res_partner_action'

# private methods

    def _build_name(self, partner, reverse_mode=False):
        if partner.is_company:
            name = partner.name or partner.lastname
            if partner.acronym and not reverse_mode:
                name = "%s (%s)" % (name, partner.acronym)
        else:
            names = [
                     partner.usual_lastname or partner.lastname,
                     partner.usual_firstname or partner.firstname or False
                    ]
            if reverse_mode:
                names = list(reversed(names))
            name = " ".join([n for n in names if n])
            if name != partner.name and not reverse_mode:
                name = "%s (%s)" % (name, partner.name)
        return name

    def _get_partner_names(self, cr, uid, ids, name, args, context=None):
        """
        ==================
        _get_partner_names
        ==================
        Recompute name fields of partners
        :param ids: partner ids
        :type ids: list
        :rparam: dictionary for all partner ids with requested computed fields
        :rtype: dict {partner_id:{'name': ...,
                                  'printable_name': ...,
                                 }}
        Note:
        Calling and result convention: Multiple mode
        """
        result = {}.fromkeys(ids, {key: False for key in ['display_name','printable_name',]})
        for partner in self.browse(cr, uid, ids, context=context):
            result[partner.id] = {
                'display_name': self._build_name(partner, reverse_mode=False),
                'printable_name': self._build_name(partner, reverse_mode=True),
            }
        return result

# data model

    _display_name_store_trigger = {
        'res.partner': (lambda self, cr, uid, ids, context=None: ids,
                        # trigger priority must be greater than 10 (i.e. priority of the store=True in partner_firstname module)
                        ['is_company', 'name', 'firstname', 'lastname', 'usual_firstname', 'usual_lastname', 'acronym', ], 20)
    }

    _columns = {
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue', select=True, track_visibility='onchange'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender', select=True, track_visibility='onchange'),
        'civil_status': fields.selection(AVAILABLE_CIVIL_STATUS, 'Civil Status', track_visibility='onchange'),
        'secondary_website': fields.char('Secondary Website', size=128, track_visibility='onchange',
                                         help="Secondary Website of Partner or Company"),
        'twitter': fields.char('Twitter', size=64, track_visibility='onchange'),
        'facebook': fields.char('Facebook', size=64, track_visibility='onchange'),
        'ldap_name': fields.char('LDAP Name', size=64, track_visibility='onchange',
                                 help="Name of the user in the LDAP"),
        'ldap_id': fields.integer('LDAP Id', track_visibility='onchange',
                                  help="ID of the user in the LDAP"),
        'usual_firstname': fields.char("Usual Firstname", track_visibility='onchange'),
        'usual_lastname': fields.char("Usual Lastname", track_visibility='onchange'),
        'printable_name': fields.function(_get_partner_names, type='char', string='Printable Name', multi="AllNames",
                                          store=_display_name_store_trigger),
        'acronym': fields.char('Acronym', select=True, track_visibility='onchange'),

        'competencies_m2m_ids': fields.many2many('thesaurus.term', 'res_partner_term_competencies_rel', id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.many2many('thesaurus.term', 'res_partner_term_interests_rel', id1='partner_id', id2='thesaurus_term_id', string='Competencies'),

        'partner_involvement_ids': fields.one2many('partner.involvement', 'partner_id', string='Partner Involvements', domain=[('active', '=', True)]),
        'partner_involvement_inactive_ids': fields.one2many('partner.involvement', 'partner_id', string='Partner Involvements', domain=[('active', '=', False)]),

        # Standard fields redefinition
        'display_name': fields.function(_get_partner_names, type='char', string='Name', multi="AllNames",
                                        store=_display_name_store_trigger),
        'website': fields.char('Main Website', size=128, track_visibility='onchange',
                               help="Main Website of Partner or Company"),
        'comment': fields.text('Notes', track_visibility='onchange'),
        'firstname': fields.char("Firstname", track_visibility='onchange'),
        'lastname': fields.char("Lastname", required=True, track_visibility='onchange'),

        # Validity period
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),

        # Special case:
        # * do not use native birthdate field, it is a char field without any control
        # * do not redefine it either, oe will silently rename twice the column (birthdate_moved12, birthdate_moved13, ...)
        #   losing its content and making the res_partner table with an astronomic number of columns !!
        'birth_date': fields.date('Birthdate', select=True, track_visibility='onchange'),
    }

    _defaults = {
        # Redefinition
        'tz': 'Europe/Brussels',
        'customer': False,
        'notification_email_send': 'none',

        # New fields
        'tongue': lambda *args: AVAILABLE_TONGUES[0][0],
    }

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if 'show_address' in context:
            res = super(res_partner, self).name_get(cr, uid, ids, context=context)
        else:
            if isinstance(ids, (int, long)):
                ids = [ids]
            res = []
            for record in self.browse(cr, uid, ids, context=context):
                name = self._build_name(record)
                if context.get('show_email') and record.email:
                    name = "%s <%s>" % (name, record.email)
                res.append((record.id, name))
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        Reset some fields to their initial values.
        """
        default = default or {}
        default.update({
            'child_ids': [],
            'user_ids': [],
            'bank_ids': [],
            'partner_involvement_ids': [],
            'partner_involvement_inactive_ids': [],

            'ldap_name': False,
            'ldap_id': False,
            'expire_date': False,
            'active': True,
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        When invalidating a partner, invalidates also its partner.involvement
        """
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals and not vals['active']:
            involvement_obj = self.pool['partner.involvement']
            involvements_ids = []
            for partner in self.browse(cr, SUPERUSER_ID, ids, context=context):
                involvements_ids += [c.id for c in partner.partner_involvement_ids]
            if involvements_ids:
                involvement_obj.button_invalidate(cr, SUPERUSER_ID, involvements_ids, context=context)
        return res

# view methods: onchange, button

    def button_invalidate(self, cr, uid, ids, context=None):
        """
        =================
        button_invalidate
        =================
        Invalidates a partner by setting
        * active to False
        * expire_date to current date
        and resetting its duplicate flags
        :rparam: True
        :rtype: boolean
        **Notes**
        If Trying to invalidate a user's partner or a company's partner:
        If the users or the company are not invalidate themselves then orm.except_orm
        """
        vals = self.get_fields_to_update(cr, uid, 'reset', context=context)
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.user_ids:
                for user in partner.user_ids:
                    if user.active:
                        raise orm.except_orm(_('Error'),
                               _('To Invalidate A Partner You First Have to Invalidate His Referenced User'))
            if partner.company_id:
                if partner.company_id.partner_id.id == partner.id:
                    raise orm.except_orm(_('Error'),
                        _('To Invalidate A Partner You First Have to Invalidate His Referenced Company'))
        vals.update({'active': False,
                     'expire_date': fields.datetime.now(),
                    })
        return self.write(cr, uid, ids, vals, context=context)

# public methods

    def create_user(self, cr, uid, login, partner_id, group_ids, context=None):
        """
        ===========
        create_user
        ===========
        Create a User related to an existing partner
        :param login: login of the new user
        :type login: char
        :param partner_id: id of the source partner
        :type partner_id: int
        :param group_ids: list of the group ids that will be associated to the user
        :type group_ids: [int]
        :raise: ERROR if partner is already a user or is a company or is not active
        """
        if not partner_id or not login:
            raise orm.except_orm(_('Error'), _('A partner and a login must be provided to create a user!'))

        partner = self.browse(cr, uid, partner_id, context=context)
        if not partner:
            raise orm.except_orm(_('Error'), _('Bad partner id: %s!') % partner_id)

        if partner.user_ids:
            raise orm.except_orm(_('Error'), _('The partner %s is already a user!') % partner.display_name)

        if partner.is_company:
            raise orm.except_orm(_('Error'), _('The partner %s cannot be a company to be associated to a user!') % partner.display_name)

        if not partner.active:
            raise orm.except_orm(_('Error'), _('The partner %s has to be active!') % partner.display_name)

        vals = group_ids and {'groups_id': [(6, 0, group_ids)]} or {}
        vals.update({
            'partner_id': partner_id,
            'login': login,
            'password': False,  # user will be authenticated by ldap or something else without password
        })

        context.update({
            'no_reset_password': True,
        })

        user_id = self.pool.get('res.users').create(cr, uid, vals, context=context)

        partner.write({'ldap_name': login}, context=context)

        return user_id

    def get_duplicate_ids(self, cr, uid, value, context=None):
        """
        =======================
        get_duplicate_ids
        =======================
        :type value: char
        :param value: value for search domain
        :rtype: [] []
        **Note**
        First Get all the partner with the ``discriminant_field`` equals to ``values``
            * If One of those partner has ``birth_date`` return will be [][all_partner_ids_found]
            * Else Return ids of Not Duplicate in first list and duplicate found into the second list
        """
        duplicate_detected_ids = []
        buffer_not_yet_decided = {}  # key: birth_date value: partner's id
        aborting = False  # if a ``birth_date`` set False then abort operation and return

        document_reset_ids, document_ids = super(res_partner, self).get_duplicate_ids(cr, uid, value, context=context)
        if document_ids:
            document_values = self.read(cr, uid, document_ids, ['birth_date'], context=context)
            birth_date_list = []  # will contain all birth date to check duplicate
            for document_value in document_values:
                if not document_value['birth_date']:
                    duplicate_detected_ids = document_ids
                    aborting = True
                    break
                # If birth_date is into the birth_date_list then is is a duplicate
                if document_value['birth_date'] in birth_date_list:
                    duplicate_detected_ids.append(document_value['id'])
                    #If this birth date is always into the buffer it is a duplicate to pop from it
                    if document_value['birth_date'] in buffer_not_yet_decided:
                        duplicate_detected_ids.append(buffer_not_yet_decided.pop(document_value['birth_date']))
                else:  # if not present into the list, add it
                    birth_date_list.append(document_value['birth_date'])
                    # add key/value into the buffer to be add it too if duplicate detected later
                    buffer_not_yet_decided.update({document_value['birth_date']: document_value['id']})
        return document_reset_ids if aborting else buffer_not_yet_decided.values(), duplicate_detected_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
