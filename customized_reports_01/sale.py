# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import decimal_precision as dp
import logging
from osv import fields, osv
from tools.translate import _


class sale_order_line(osv.osv):
    """
Inherit sale_order_line to allow users to enter
price_unit_uos or price_unit (uom) and calculate the other values accordingly.
"""
    _inherit = "sale.order.line"

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = super(sale_order_line, self)._amount_line(cr, uid, ids,
                                                        field_name, arg,
                                                        context=context)
#         tax_obj = self.pool.get('account.tax')
#         cur_obj = self.pool.get('res.currency')
#         res = {}
#         if context is None:
#             context = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             if line.product_uos:
#                 base_price = line.price_unit_uos
#                 qty = line.product_uos_qty
#             else:
#                 base_price = line.price_unit
#                 qty = line.product_uom_qty
#             price = base_price * (1 - (line.discount or 0.0) / 100.0)
#             taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, qty,
#                                         line.order_id.partner_invoice_id.id,
#                                         line.product_id,
#                                         line.order_id.partner_id)
#             cur = line.order_id.pricelist_id.currency_id
#             res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal': fields.function(
            _amount_line, string='Subtotal',
            digits_compute = dp.get_precision('Account')),
    }

sale_order_line()