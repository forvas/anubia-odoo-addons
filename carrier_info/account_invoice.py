# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _


class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'reception_in_report': fields.boolean(
            'Show reception fields in reports',
            help=("Check if you want reception fields to be printed in "
                  "reports.")),
        'incoterm': fields.many2one(
            'stock.incoterms',
            'Incoterm',
            help=("Incoterm which stands for 'International Commercial terms' "
                  "implies its a series of sales terms which are used in the "
                  "commercial transaction.")),
        'carrier_in_report': fields.boolean(
            'Show carrier in reports',
            help="Check if you want carrier info to be shown in reports."),
        'carrier_id': fields.many2one(
            'res.partner',
            'Carrier',
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
        'reception_in_report': False,
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

account_invoice()
