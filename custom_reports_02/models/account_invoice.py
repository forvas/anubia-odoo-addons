# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice' 
    #Do not touch _name it must be same as _inherit
    #_name = 'account.invoice' 
    
    print_taxes = fields.Boolean(string="Print tax details",
                                 readonly=False,
                                 default=False,
                                 help="Print tax details in invoice report.")
