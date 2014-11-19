# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import tools
# from osv import fields,osv
from openerp.osv import fields, orm


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _columns = {
        'country_id': fields.many2one(
            'res.country', 'Country', required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'address_invoice_id': fields.many2one(
            'res.partner.address', 'Invoice Address', required=True,
            readonly=True, states={'draft': [('readonly', False)]}),
    }

    def onchange_address_invoice_id(self, cr, uid, ids,
                                    address_invoice_id=False,
                                    context=None):
        value = {}
        if not context:
            context = {}
        warning = {}

        if not address_invoice_id:
            value.update({'country_id': False})
        else:
            address_invoice_obj = self.pool.get('res.partner.address')
            address_invoice = address_invoice_obj.browse(cr, uid,
                                                         address_invoice_id,
                                                         context=context)
            value.update({'country_id': address_invoice.country_id.id})

        return {'value': value, 'context': context}

account_invoice()
