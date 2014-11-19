# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import decimal_precision as dp
import logging
# from osv import fields, osv
from openerp.osv import fields, orm
from tools.translate import _
from tools import float_compare


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sale order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order,
                                                                lines, context)
        # Will add the country_id field to the new invoice, if possible
        address_obj = self.pool.get('res.partner.address')
        address = address_obj.browse(cr, uid, order.partner_invoice_id.id,
                                     context=context)
        country_id = address and address.country_id.id or False
        
        invoice_vals.update({
            'country_id': country_id,
        })

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))

        return invoice_vals
