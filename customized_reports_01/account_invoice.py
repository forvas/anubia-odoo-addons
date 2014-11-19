# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import time
from lxml import etree
import decimal_precision as dp
import logging
import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return super(account_invoice_line, self)._amount_line(cr, uid, ids,
                                                              prop,
                                                              unknow_none,
                                                              unknow_dict)
#         res = {}
#         tax_obj = self.pool.get('account.tax')
#         cur_obj = self.pool.get('res.currency')
#         local_context = {}
#         for line in self.browse(cr, uid, ids):
#             price = line.price_unit * (1-(line.discount or 0.0)/100.0)
#             local_context['tax_calculation_rounding_method'] = (
#                     line.invoice_id.tax_calculation_rounding_method)
#             taxes = tax_obj.compute_all(
#                 cr, uid, line.invoice_line_tax_id, price, line.quantity,
#                 product=line.product_id,
#                 address_id=line.invoice_id.address_invoice_id,
#                 partner=line.invoice_id.partner_id,
#                 context=local_context)
#             res[line.id] = taxes['total']
#             if line.invoice_id:
#                 cur = line.invoice_id.currency_id
#                 res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
#         return res

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal',
            type="float", digits_compute=dp.get_precision('Sale Price'),
            store=True),
    }
    
account_invoice_line()
