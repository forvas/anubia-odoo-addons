# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)


class event_event(orm.Model):
    _inherit = 'account.invoice'

    def invoice_print(self, cr, uid, ids, context=None):
        ''' This function prints the invoice and mark it as sent, so that we
        can see more easily the next step of the workflow. '''
        assert len(ids) == 1, 'This option should only be used for a single ' \
                              'id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
            'ids': ids,
            'model': 'account.invoice',
            'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.invoice.custom',
            'datas': datas,
            'nodestroy': True,
        }
