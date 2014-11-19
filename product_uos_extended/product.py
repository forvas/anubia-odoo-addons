# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import decimal_precision as dp
import logging
from osv import osv, fields
from tools.translate import _


class product_uom(osv.osv):
    _inherit = 'product.uom'

    def _qty_swap_uom_uos(self, cr, uid,
                          product_id=None, swap_type='uom2uos',
                          uom1_id=False, uom1_qty=False,
                          uom2_id=False, context=None):
        """
        Computes the quantity of a product between:
            uom (or same category) <--> uos (or same category)
            a) swap_type='uom2uos': from a uom to a uos.
            b) swap_type='uos2uom': from a uos to a uom.
            NOTE: swap_type: ('uom2uos', 'uos2uom')
        Internally makes three steps:
            1) Calculates qty(from_uom1) -> qty(default_uom1)
            2) Calculates qty(default_uom1) -> qty(default_uom2) with uos_coeff
            3) Calculates qty(default_uom2) -> qty(to_uom2)
            NOTE: default_uom1 and default_uom2 are product.template uom,uos
        """
        if not product_id or not uom1_id or not uom1_qty or not uom2_id:
            return uom1_qty

        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)
        if not product or not product.uos_id or not product.uos_coeff:
            return uom1_qty

        def_uom_id = product.uom_id.id
        uos_coeff = product.uos_coeff
        def_uos_id = product.uos_id.id

        if swap_type == 'uom2uos':
            def_uom1_id = product.uom_id.id
            def_uom2_id = product.uos_id.id
            coeff = product.uos_coeff
        elif swap_type == 'uos2uom':
            def_uom1_id = product.uos_id.id
            def_uom2_id = product.uom_id.id
            try:
                coeff = 1 / product.uos_coeff
            except ZeroDivisionError:
                return uom1_qty

        product_uom_obj = self.pool.get('product.uom')
        def_uom1_qty = self._compute_qty(cr, uid,
                                         uom1_id, uom1_qty, def_uom1_id)
        def_uom2_qty = def_uom1_qty * coeff
        uom2_qty = product_uom_obj._compute_qty(cr, uid,
                                                def_uom2_id,
                                                def_uom2_qty,
                                                uom2_id)
        return uom2_qty

    def _price_swap_uom_uos(self, cr, uid,
                            product_id=None, swap_type='uom2uos',
                            uom1_id=False, uom1_price=False,
                            uom2_id=False, context=None):
        """
        Computes the quantity of a product:
            a) swap_type='uom2uos': from a uom to a uos.
            b) swap_type='uos2uom': from a uos to a uom.
            NOTE: swap_type: ('uom2uos', 'uos2uom')
        Internally makes three steps:
            1) Calculates price(from_uom1) -> price(default_uom1)
            2) Calculates price(def_uom1) -> price(def_uom2) with uos_coeff
            3) Calculates price(def_uom2) -> price(to_uom2)
            NOTE: default_uom1 and default_uom2 are product.template uom,uos
        """
        if not product_id or not uom1_id or not uom1_price or not uom2_id:
            return uom1_price
        if not swap_type or swap_type not in ('uom2uos', 'uos2uom'):
            return uom1_price

        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)

        if not product or not product.uos_id or not product.uos_coeff:
            return uom1_price

        if swap_type == 'uom2uos':
            def_uom1_id = product.uom_id.id
            def_uom2_id = product.uos_id.id
            try:
                coeff = 1 / product.uos_coeff
            except ZeroDivisionError:
                return uom1_price
        elif swap_type == 'uos2uom':
            def_uom1_id = product.uos_id.id
            def_uom2_id = product.uom_id.id
            coeff = product.uos_coeff

        product_uom_obj = self.pool.get('product.uom')
        # From uom1 to def_uom1
        def_uom1_price = product_uom_obj._compute_price(cr, uid,
                                                        uom1_id, uom1_price,
                                                        def_uom1_id)
        # From def_uom1 to def_uom2
        def_uom2_price = def_uom1_price * coeff
        # From def_uom2 to uom2
        uom2_price = product_uom_obj._compute_price(cr, uid,
                                                    def_uom2_id,
                                                    def_uom2_price,
                                                    uom2_id)
        return uom2_price

product_uom()


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'list_price_uos': fields.float(
            'Sale Price per UoS',
            digits_compute=dp.get_precision('Sale Price'),
            help=("Base price (per Unit of Sale, if"
                  " specified) for computing the customer"
                  " price. Sometimes called the catalog"
                  " price."),
            readonly=False),
        'list_price_uos_dummy': fields.related(
            'list_price_uos', type="float",
            readonly=True, store=False, string='Sale Price per UoS',
            digits_compute=dp.get_precision('Sale Price')),
        'cancel_uos_coeff': fields.boolean(
            'Cancel onchange_uos_coeff'),
        'cancel_list_price_uom': fields.boolean(
            'Cancel onchange_price_unit_uom'),
        'cancel_list_price_uos': fields.boolean(
            'Cancel onchange_price_unit_uos'),
    }
    _defaults = {
        'list_price_uos': lambda *a: 1.0,
    }

    def onchange_uos(self, cr, uid, ids,
                     uom_id=None, uos_id=None, uos_coeff=1.0,
                     list_price=1.0, list_price_uos=1.0,
                     context=None):
        """ Updates list_price or list_price_uos """
        logger = logging.getLogger(__name__)
        logger.debug('>>>> product.onchange_uos:\n'
                     '\t uom_id:         {}\n'
                     '\t uos_id:         {}\n'
                     '\t uos_coeff:      {}\n'
                     '\t list_price:     {}\n'
                     '\t list_price_uos: {}\n'
                     '\n'.format(uom_id, uos_id, uos_coeff,
                                 list_price, list_price_uos))
        value = {}
        if not context:
            context = {}

#         if not list_price or list_price <= float(0):
#             new_list_price_uom = 1.0
#         else:
#             new_list_price_uom = float(list_price)
        new_list_price_uom = float(list_price)
        if not uos_id:
            new_uos_coeff = False  # 1.0
            new_list_price_uos = False  # new_list_price_uom
        else:
            if not uos_coeff or uos_coeff <= float(0):
                new_uos_coeff = 1.0
            else:
                new_uos_coeff = float(uos_coeff)
            new_list_price_uos = list_price_uos or new_list_price_uom  # 1.0
            new_list_price_uom = new_list_price_uos * new_uos_coeff
        
        value.update({
            'cancel_uos_coeff': (new_uos_coeff != uos_coeff),
            'cancel_list_price_uom': (new_list_price_uom != list_price),
            'cancel_list_price_uos': (new_list_price_uos != list_price_uos),
            'uos_coeff': new_uos_coeff,
            'list_price': new_list_price_uom,
            'list_price_uos': new_list_price_uos,
        })
        return {'value': value, 'context': context}

    def onchange_uos_coeff(self, cr, uid, ids,
                           uom_id=None, uos_id=None, uos_coeff=1.0,
                           list_price=1.0, list_price_uos=1.0,
                           cancel_uos_coeff=False,
                           cancel_list_price_uom=False,
                           cancel_list_price_uos=False,
                           context=None):
        """ Updates list_price or list_price_uos """
        logger = logging.getLogger(__name__)
        logger.debug('>>>> product.onchange_uos_coeff:\n'
                     '\t uom_id:         {}\n'
                     '\t uos_id:         {}\n'
                     '\t uos_coeff:      {}\n'
                     '\t list_price:     {}\n'
                     '\t list_price_uos: {}\n'
                     '\n'.format(uom_id, uos_id, uos_coeff,
                                 list_price, list_price_uos))
        value = {}
        if not context:
            context = {}
        # To avoid recursive triggers
        if cancel_uos_coeff:
            value.update({
                'cancel_uos_coeff': False,
            })
            return {'value': value, 'context': context}
# 
#         if not list_price or list_price <= 0.0:
#             new_list_price_uom = 1.0
#         else:
#             new_list_price_uom = float(list_price)
        new_list_price_uom = float(list_price)
        if not uos_id:
            new_uos_coeff = False  # 1.0
            new_list_price_uos = False  # new_list_price_uom
        else:
            if not uos_coeff or float(uos_coeff) <= float(0):
                new_uos_coeff = 1.0
                cancel_uos_coeff = False
            else:
                new_uos_coeff = float(uos_coeff)
                cancel_uos_coeff = (new_uos_coeff != float(uos_coeff))
                
            if not list_price_uos or list_price_uos <= 0.0:
                new_list_price_uos = new_list_price_uom
            else:
                new_list_price_uos = float(list_price_uos)  # 1.0
            new_list_price_uom = new_list_price_uos * new_uos_coeff

        value.update({
            'cancel_uos_coeff': cancel_uos_coeff,
            'cancel_list_price_uom': (new_list_price_uom != list_price),
            'cancel_list_price_uos': (new_list_price_uos != list_price_uos),
            'uos_coeff': new_uos_coeff,
            'list_price': new_list_price_uom,
            'list_price_uos': new_list_price_uos,
        })
        return {'value': value, 'context': context}

    def onchange_list_price(self, cr, uid, ids,
                            uom_id=None, uos_id=None, uos_coeff=1.0,
                            list_price=1.0, list_price_uos=1.0,
                            cancel_uos_coeff=False,
                            cancel_list_price_uom=False,
                            cancel_list_price_uos=False,
                            context=None):
        """ Updates list_price_uos if needed """
        logger = logging.getLogger(__name__)
        logger.debug('>>>> product.onchange_list_price:\n'
                     '\t uom_id:         {}\n'
                     '\t uos_id:         {}\n'
                     '\t uos_coeff:      {}\n'
                     '\t list_price:     {}\n'
                     '\t list_price_uos: {}\n'
                     '\n'.format(uom_id, uos_id, uos_coeff,
                                 list_price, list_price_uos))
        value = {}
        if not context:
            context = {}
        # To avoid recursive triggers
        if cancel_list_price_uom:
            value.update({
                'cancel_list_price_uom': False,
            })
            return {'value': value, 'context': context}

        if list_price is None or list_price < float(0):
            new_list_price_uom = 1.0
            cancel_list_price_uom = False
        else:
            new_list_price_uom = float(list_price)
            cancel_list_price_uom = (new_list_price_uom != list_price)

        if not uos_id:
#             new_uos_coeff = False  # 1.0
            new_list_price_uos = False  # new_list_price_uom
        else:
            # uos_coeff should have been checked already
            new_list_price_uos = new_list_price_uom / float(uos_coeff)

        value.update({
            'cancel_list_price_uom': cancel_list_price_uom,
            'cancel_list_price_uos': (new_list_price_uos != list_price_uos),
            'list_price': new_list_price_uom,
            'list_price_uos': new_list_price_uos,
        })
        return {'value': value, 'context': context}

    def onchange_list_price_uos(self, cr, uid, ids,
                                uom_id=None, uos_id=None, uos_coeff=1.0,
                                list_price=1.0, list_price_uos=1.0,
                                cancel_uos_coeff=False,
                                cancel_list_price_uom=False,
                                cancel_list_price_uos=False,
                                context=None):
        """ Updates list_price """
        logger = logging.getLogger(__name__)
        logger.debug('>>>> product.onchange_list_price_uos:\n'
                     '\t uom_id:         {}\n'
                     '\t uos_id:         {}\n'
                     '\t uos_coeff:      {}\n'
                     '\t list_price:     {}\n'
                     '\t list_price_uos: {}\n'
                     '\n'.format(uom_id, uos_id, uos_coeff,
                                 list_price, list_price_uos))
        value = {}
        if not context:
            context = {}
        # To avoid recursive triggers
        if cancel_list_price_uos:
            value.update({
                'cancel_list_price_uos': False,
                'list_price_uos_dummy': list_price_uos,
            })
            return {'value': value, 'context': context}

        # We should only reach here if uos_id and uos_coeff are defined
#         if not uos_id:
#             new_list_price_uos = False  # new_list_price_uom
#             new_list_price_uom = list_price
#         else:
        if list_price_uos is None or list_price_uos < float(0):
            new_list_price_uos = 1.0
            cancel_list_price_uos = False
        else:
            new_list_price_uos = float(list_price_uos)
            cancel_list_price_uos = (new_list_price_uos != list_price_uos)
        # uos_coeff should have been checked already
        new_list_price_uom = new_list_price_uos * float(uos_coeff)

        value.update({
            'cancel_list_price_uom': (new_list_price_uom != list_price),
            'cancel_list_price_uos': cancel_list_price_uos,
            'list_price': new_list_price_uom,
            'list_price_uos': new_list_price_uos,
            'list_price_uos_dummy': new_list_price_uos,
        })
        return {'value': value, 'context': context}

product_product()
