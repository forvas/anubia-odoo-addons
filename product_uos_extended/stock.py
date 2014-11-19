# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from osv import fields, osv, orm
from tools.translate import _


class stock_move(osv.osv):
    _inherit = "stock.move"

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        super(stock_move, self).onchange_quantity(cr, uid, ids,
                                                  product_id, product_qty,
                                                  product_uom, product_uos)
        result = {
            'product_uos_qty': 0.00
        }

        if (not product_id) or (product_qty <= 0.0):
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty

        return {'value': result}

    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty,
                              product_uos, product_uom):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_uos_qty: Changed UoS Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        super(stock_move, self).onchange_uos_quantity(cr, uid, ids, product_id,
                                                      product_uos_qty,
                                                      product_uos, product_uom)
        result = {
            'product_qty': 0.00
        }

        if (not product_id) or (product_uos_qty <= 0.0):
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_qty'] = product_uos_qty / uos_coeff['uos_coeff']
        else:
            result['product_qty'] = product_uos_qty

        return {'value': result}

stock_move()
