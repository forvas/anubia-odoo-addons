# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import decimal_precision as dp
import logging
from osv import fields, osv
from tools.translate import _


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'reception_in_report': fields.boolean(
            'Show reception fields in reports',
            help=("Check if you want reception fields to be printed in "
                  "reports.")),
        'carrier_in_report': fields.boolean(
            'Show carrier in reports',
            help="Check if you want carrier info to be shown in reports."),
        'carrier_id': fields.many2one(
            'res.partner',
            'Carrier',
            domain="[('carrier','=',True)]",
            help='Select here the carrier partner.'),
        'carrier_ref': fields.char(
            'Carrier reference',
            size=64,
            help='Carrier reference for this order.'),
        'carrier_vehicle': fields.text(
            'Vehicle data',
            help=("Any data related to the vehicles, like plates, "
                  "maximum weight, ship name, etc.")),
        'carrier_notes': fields.text(
            'Carrier notes',
            help=("Any other data regarding the carrier.")),
    }
    _defaults = {
        'reception_in_report': True,
        'carrier_in_report': True,
    }

    def onchange_carrier_id(self, cr, uid, ids, carrier_id=False):
        value = {}
        if carrier_id:
            carrier_obj = self.pool.get('res.partner')
            carrier = carrier_obj.browse(cr, uid, carrier_id)
            value['carrier_vehicle'] = carrier.carrier_vehicle or ''
            value['carrier_notes'] = carrier.carrier_notes or ''
        else:
            value['carrier_vehicle'] = ''
            value['carrier_notes'] = ''
        return {'value': value}

    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_id = super(sale_order, self)._make_invoice(cr, uid,
                                                       order, lines, context)
        inv_obj = self.pool.get('account.invoice')
        inv_obj.write(cr, uid, [inv_id],
                      {'incoterm': order.incoterm.id},
                      context=context)
        if order.carrier_id:
            inv_obj.write(cr, uid, [inv_id],
                          {'carrier_id': order.carrier_id.id},
                          context=context)
        inv_obj.write(cr, uid, [inv_id],
                      {'carrier_ref': order.carrier_ref},
                      context=context)
        inv_obj.write(cr, uid, [inv_id],
                      {'carrier_vehicle': order.carrier_vehicle},
                      context=context)
        inv_obj.write(cr, uid, [inv_id],
                      {'carrier_notes': order.carrier_notes},
                      context=context)
        inv_obj.write(cr, uid, [inv_id],
                      {'carrier_in_report': order.carrier_in_report},
                      context=context)
        return inv_id

    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_dict = super(sale_order,
                          self)._prepare_order_picking(cr, uid, order, context)
        pick_dict.update({
            'incoterm': order.incoterm.id or None,
            'carrier_id': order.carrier_id.id or None,
            'carrier_ref': order.carrier_ref or '',
            'carrier_vehicle': order.carrier_vehicle or '',
            'carrier_notes': order.carrier_notes or '',
            'carrier_in_report': order.carrier_in_report or '',
        })
        return pick_dict

sale_order()
