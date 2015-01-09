# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from osv import fields, osv


class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _order = 'date_order desc, id desc'
