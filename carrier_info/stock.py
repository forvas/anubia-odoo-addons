# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from osv import fields, osv


#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = 'stock.picking'

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
            domain="[('carrier','=',True)]",
            help='Select here the carrier partner.'),
        'carrier_ref': fields.char(
            'Carrier reference',
            size=64,
            help='Carrier reference for this picking list.'),
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

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id,
                         context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice',
                   'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        invoice_vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context)
        invoice_vals['incoterm'] = picking.incoterm.id or None
        invoice_vals['carrier_id'] = picking.carrier_id.id or None
        invoice_vals['carrier_ref'] = picking.carrier_ref or ''
        invoice_vals['carrier_vehicle'] = picking.carrier_vehicle or ''
        invoice_vals['carrier_notes'] = picking.carrier_notes or ''
        return invoice_vals

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

stock_picking()
