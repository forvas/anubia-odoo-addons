# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from osv import osv
from osv import fields


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'carrier': fields.boolean(
            'Carrier',
            help="Check if this partner is a carrier."),
        'carrier_vehicle': fields.text(
            'Vehicle data',
            help=("Any data related to the vehicles, like plates, "
                  "maximum weight, ship name, etc.")),
        'carrier_notes': fields.text(
            'Carrier notes',
            help=("Any other data regarding the carrier.")),
    }
    _defaults = {
        'carrier': False,
    }

res_partner()
