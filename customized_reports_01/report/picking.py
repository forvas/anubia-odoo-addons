# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import time
from report import report_sxw
from osv import osv
import pooler


class picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal': self._get_qtytotal,
        })

    def _get_qtytotal(self, move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total += move.product_qty
        return {'quantity': total, 'uom': uom}

report_sxw.report_sxw('report.stock.picking.list', 'stock.picking',
                      'addons/customized_reports_01/report/picking.rml',
                      parser=picking)
