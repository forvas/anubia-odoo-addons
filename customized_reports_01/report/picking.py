# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from collections import defaultdict


class picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qtytotal': self._get_qtytotal,
            'stock_moves_grouped_by_name': self._stock_moves_grouped_by_name,
        })

    def _get_qtytotal(self, move_lines):
        total = 0.0
        uom = move_lines[0].product_uom.name
        for move in move_lines:
            total += move.product_qty
        return {'quantity': total, 'uom': uom}

    def _stock_moves_grouped_by_name(self):
        ids = pooler.get_pool(self.cr.dbname).get('stock.move').search(
            self.cr, self.uid, [('picking_id', '=',
                                 self.localcontext['active_id'])],
            context=self.localcontext)
        stock_moves = pooler.get_pool(self.cr.dbname).get('stock.move').browse(
            self.cr, self.uid, ids, context=self.localcontext)

        groups = defaultdict(list)
        for obj in stock_moves:
            groups[obj.name].append(obj)
        grouped_list_by_name = groups.values()

        stock_moves_grouped_by_name = []
        for same_name_obj_list in grouped_list_by_name:
            for obj in same_name_obj_list:
                if obj == same_name_obj_list[0]:
                    continue
                same_name_obj_list[0].product_qty += obj.product_qty
            stock_moves_grouped_by_name.append(same_name_obj_list[0])
        return stock_moves_grouped_by_name

report_sxw.report_sxw('report.stock.picking.list.custom', 'stock.picking',
                      'addons/customized_reports_01/report/picking.rml',
                      parser=picking)
