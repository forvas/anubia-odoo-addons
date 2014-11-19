# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import tools
# from osv import fields,osv
from openerp.osv import fields, orm


class res_partner_address(orm.Model):
    _inherit = 'res.partner.address'

    _columns = {
        # Add the required=True condition
        'country_id': fields.many2one('res.country', 'Country', required=True),
    }

res_partner_address()
