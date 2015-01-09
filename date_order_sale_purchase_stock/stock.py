# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from osv import fields, osv


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _order = 'date desc, id desc'
