# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from osv import osv,fields
import decimal_precision as dp


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                line_price_unit_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                for c in self.pool.get('account.tax').compute(cr, uid, line.taxes_id, line_price_unit_discounted, line.product_qty, order.partner_address_id.id, line.product_id, order.partner_id):
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(
            _amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            },
            multi="sums",
            help="The amount without tax"),
        'amount_tax': fields.function(
            _amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            },
            multi="sums",
            help="The tax amount"),
        'amount_total': fields.function(
            _amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            },
            multi="sums",
            help="The total amount"),
    }

purchase_order()


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            cur = line.order_id.pricelist_id.currency_id
            disc = (line.discount or 0.0)
            calc = line.price_unit * line.product_qty * (1 - disc / 100.0)
            res[line.id] = cur_obj.round(cr, uid, cur, calc)
        return res

    _columns = {
        'discount': fields.float('Discount (%)',
                          digits_compute=dp.get_precision('Purchase Price')),
        'price_subtotal': fields.function(_amount_line, method=True,
                          string='Subtotal',
                          digits_compute=dp.get_precision('Purchase Price')),
    }

purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

