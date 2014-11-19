# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid,
                               picking, partner, inv_type, journal_id, context)
#         invoice_vals['comment'] = picking.note or ''
        invoice_vals['name'] = ''
        return invoice_vals

stock_picking()
