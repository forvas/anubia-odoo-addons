# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import time
from lxml import etree
import decimal_precision as dp
import logging
import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _price_unit_default(self, cr, uid, context=None):
        super(account_invoice_line, self)._price_unit_default(cr, uid, context)
        if context is None:
            context = {}
        if context.get('check_total', False):
            t = context['check_total']
            for l in context.get('invoice_line', {}):
                if isinstance(l, (list, tuple)) and len(l) >= 3 and l[2]:
                    tax_obj = self.pool.get('account.tax')
                    p = l[2].get('price_unit', 0) * (1 - l[2].get(
                        'discount', 0) / 100.0)
                    t = t - (p * l[2].get('quantity'))
                    taxes = l[2].get('invoice_line_tax_id')
                    if len(taxes[0]) >= 3 and taxes[0][2]:
                        taxes = tax_obj.browse(cr, uid, list(taxes[0][2]))
                        for tax in tax_obj.compute_all(
                                cr, uid, taxes, p,
                                l[2].get('quantity'),
                                context.get('address_invoice_id', False),
                                l[2].get('product_id', False),
                                context.get('partner_id', False))['taxes']:
                            t = t - tax['amount']
            return t
        return 0

    def _get_uos_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product',
                                                'product_uos_unit')
            return result[1]
        except Exception, ex:
            return False

    def _has_uos(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product',
                                                'product_uos_unit')
            has_uos = result[1] and True or False
            return has_uos
        except Exception, ex:
            return False

    _columns = {
        'uos_id': fields.many2one(
            'product.uom', 'Unit of Measure',
            required=True, ondelete='set null'),
        'product_has_uos': fields.boolean(
            'Product has UoS defined',
            help=("Checked if selected product has a defined UoS "
                  "(Unit of Sale).")),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure',
                                  required=True, ondelete='set null'),
        'quantity_uom': fields.float(
            'Quantity (UoM)',
            required=True,
            digits_compute=dp.get_precision('Product UoM')),
        'price_unit_uom': fields.float(
            'Unit Price (UoM)',
            required=True,
            digits_compute=dp.get_precision('Sale Price')),
        'uos_id_dummy': fields.related(
            'uos_id', type="many2one", relation="product.uom",
            readonly=True, store=False, string='Unit of Sale'),
        'quantity': fields.float(
            'Quantity',
            # required=True),
            required=True,
            digits_compute=dp.get_precision('Product UoS')),
        'quantity_dummy': fields.related(
            'quantity', type="float",
            readonly=True, store=False, string='Quantity (UoS)',
            digits_compute=dp.get_precision('Product UoS')),
        'price_unit_dummy': fields.related(
            'price_unit', type="float",
            readonly=True, store=False, string='Unit Price (UoS)',
            digits_compute=dp.get_precision('Sale Price')),
        'cancel_uom': fields.boolean(
            'Cancel onchange_uom_id'),
        'cancel_uom_qty': fields.boolean(
            'Cancel onchange_quantity_uom'),
        'cancel_uom_price': fields.boolean(
            'Cancel onchange_price_unit_uom'),
        'cancel_uos': fields.boolean(
            'Cancel onchange_uos_id'),
        'cancel_uos_qty': fields.boolean(
            'Cancel onchange_quantity'),
        'cancel_uos_price': fields.boolean(
            'Cancel onchange_price_unit'),
        # NOTE: [0]
        # ---------
        # With some extra fields (starting with 'cancel_') we manage to
        # avoid mutual recursive triggers amongst fields that change
        # one another.
        # A) If this change is a result of direct manual user's intervention,
        #    such flag should be False, and normal execution should continue.
        # B) Otherwise, being a result other onchange functions started
        #    by this one, such flag should be True. In that case, further
        #    processing of this onchange is skipped and the flag reset to False
        #    (thus allowing being modified by changes in other fields).

        # NOTE: [1]
        # ---------
        # Dummy fields are needed for when product has no UoS and it is cloned
        # from UoM and the user must not be able to modify them, but we need
        # to store it's data.
        # Standard module use UoS fields only... but they can be populated
        # with UoM or UoS if created from a Sales Order... but only from
        # product.uom if creating a manual invoice. Even more, they do not
        # use product.uom.factor (or product.uom.factor_inv) if you choose
        # a different unit in the same category.
        # Thus, standard modules mix the whole UoM/UoS concept, and prevent
        # user to distinguish among them in invoices.
        # This module tries to make the UoM/UoS concept easy and understandable
        # for the final user. He will see always:
        # * UoM fields (quantity, unit, price_unit): always modifiable
        # * UoS fields (quantity, unit, price_unit): modifiable if product has
        #   a defined product.uos and product.uos_coeff
        # This allows to modify one of this values and autocalculate the rest.
        # This takes care of units within the same category and their factor.
    }

    _defaults = {
        'cancel_uom': False,
        'cancel_uom_qty': False,
        'cancel_uom_price': False,
        'cancel_uos': True,
        'cancel_uos_qty': True,
        'cancel_uos_price': True,
        'product_has_uos': _has_uos,
        'quantity_uom': _get_uos_id,
        'price_unit_uom': _price_unit_default,
        'uos_id': _get_uos_id,
    }

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          address_invoice_id=False, currency_id=False,
                          context=None, company_id=None,
                          uom_id=False, qty_uom=1.0, price_unit_uom=1.0):
        logger = logging.getLogger(__name__)
        logger.debug('>>>> product_id_change -> Entered! context: \n'
                     '{}'.format(context))
        logger.debug('\n>>>> product_id_change -> price_unit(0): \n'
                     '{}'.format(price_unit))
        # Variable naming that makes a little more sense:
        uos_id = uom
        qty_uos = float(qty)
        price_unit_uos = float(price_unit)

        if company_id is None:
            company_id = context.get('company_id', False)
        else:
            company_id = company_id
        context = dict(context)
        context.update({'company_id': company_id})
        # Call super() for compatibility
        res = super(account_invoice_line, self).product_id_change(
            cr, uid, ids, product, uom, qty, name, type, partner_id,
            fposition_id, price_unit, address_invoice_id, currency_id,
            context=context)
            # , company_id)

        # Will reset quantity_uom to 1.0 as a initial value
        res['value'].update({'quantity_uom': 1.0, })
        if not product:
            res['domain'].update({'uom_id': [('category_id', '!=', False)],
                                  'uos_id': [('category_id', '!=', False)]
                                  })
            res['value'].update({'product_has_uos': False,
                                 # 'cancel_uos': True,
                                 # 'cancel_uos_qty': True,
                                 # 'cancel_uos_price': True,
                                 'uos_id': False,
                                 # 'uos_id_dummy': False,  # Redundant
                                 'uom_id': False,
                                 # 'quantity_uom': 1.0,
                                 'price_unit_uom': 0.0,
                                 })
            return res

        # If there is a product defined:
        product_obj = self.pool.get('product.product')
        prod = product_obj.browse(cr, uid, product, context=context)

        new_uom_id = prod.uom_id and prod.uom_id.id or False
        new_uos_id = prod.uos_id and prod.uos_id.id or new_uom_id
        has_uos = prod.uos_id and True or False

        logger.debug(('\n\n\n\n>>>> product_id_change -> \n'
                      '\t prod.uom_id: {}\n'
                      '\t uom        : {}\n'
                      '\t new_uom_id    : {}\n'
                      '\t new_uos_id    : {}\n'
                      '\t has_uos    : {}\n').format(prod.uom_id, uom,
                                                     new_uom_id, new_uos_id,
                                                     has_uos))
        logger.debug(('\n\n\n\n>>>> product_id_change -> \n'
                      '\t new_uom_id        : {}\n').format(new_uom_id))
        logger.debug(('\n\n\n\n>>>> product_id_change -> \n'
                      '\t prod.uom_id.id : {}\n').format(prod.uom_id.id))

        res['value'].update({'product_has_uos': has_uos,
                             # 'cancel_uos': not has_uos,
                             # 'cancel_uos_qty': not has_uos,
                             # 'cancel_uos_price': not has_uos,
                             })
        product_uom_obj = self.pool.get('product.uom')
        new_qty_uom = 1.0
        new_qty_uos = product_uom_obj._qty_swap_uom_uos(cr, uid,
                                                        product, 'uom2uos',
                                                        new_uom_id,
                                                        new_qty_uom,
                                                        new_uos_id)
        qty_uom_real = product_uom_obj._compute_qty(cr, uid,
                                                    new_uom_id, new_qty_uom,
                                                    prod.uom_id.id)

        new_price_unit_uom, pu_uom_warning = self._price_unit_get(
            cr, uid, product, new_uom_id, qty_uom_real, type, partner_id,
            currency_id, context=context)

        new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
            cr, uid, product, 'uom2uos', new_uom_id, new_price_unit_uom,
            new_uos_id)

        logger.debug(('\n\n\n\n>>>> product_id_change -> '
                      '  new_price_unit_uos: {}\n'
                      '  old price_unit    : {}\n'
                      '  new_price_unit_uom: {}\n'
                      '  ').format(new_price_unit_uom, price_unit,
                                   new_price_unit_uom))
        # result['price_unit'] = price_unit_uom  # might be False
        warning = {}
        warning.update(pu_uom_warning)
        res['value'].update({'uom_id': new_uom_id,
                             'uos_id': new_uos_id,
                             # 'uos_id_dummy': new_uos_id.id,
                             'quantity_uom': new_qty_uom,
                             'quantity': new_qty_uos,
                             'price_unit_uom': new_price_unit_uom,
                             'price_unit': new_price_unit_uos,
                             })

        # Due to the complexity of chained changes involved, it is easier
        # to avoid them completely and update all needed changes in this
        # function only
        # NOTE: Cannot force it to True because if value doesn't change
        #       the flag will affect next change, uncontrollably
        res['value'].update({
            'cancel_uom': (new_uom_id != uom_id),
            'cancel_uom_qty': (new_qty_uom != qty_uom),
            'cancel_uom_price': (new_price_unit_uom != price_unit_uom),
            'cancel_uos': (new_uos_id != uos_id),
            'cancel_uos_qty': (new_qty_uos != qty_uos),
            'cancel_uos_price': (new_price_unit_uos != price_unit_uos),
        })

        # Restrain the UoM drop menu to the its category
        prod_uom_cat = prod.uom_id and prod.uom_id.category_id.id or False
        if prod_uom_cat:
            res['domain'].update({
                'uom_id': [('category_id', '=', prod_uom_cat)]
            })
        else:
            res['domain'].update({'uom_id': [('category_id', '!=', False)]})
        # Restrain the UoS drop menu to the its category
        prod_uos_cat = prod.uos_id and prod.uos_id.category_id.id or \
            prod_uom_cat

        if prod_uos_cat:
            res['domain'].update({
                'uos_id': [('category_id', '=', prod_uos_cat)]
            })
        else:
            res['domain'].update({'uos_id': [('category_id', '!=', False)]})
        return res

    # ---- UoM
    def onchange_quantity_uom(self, cr, uid, ids,
                              product_id=None,
                              qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                              qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                              type='out_invoice', partner_id=False,
                              currency_id=False, product_has_uos=False,
                              cancel_uom=False,
                              cancel_uom_qty=False,
                              cancel_uom_price=False,
                              cancel_uos=False,
                              cancel_uos_qty=False,
                              cancel_uos_price=False,
                              context=None):
        """Captures changes in quantity (UoM) and changes accordingly
        the quantity (UoS), if needed."""
        logger = logging.getLogger(__name__)
        logger.debug('\n'
                     'onchange_quantity_uom:\n'
                     '  cancel_uom       = {}\n'
                     '  cancel_uom_qty   = {}\n'
                     '  cancel_uom_price = {}\n'
                     '  cancel_uos       = {}\n'
                     '  cancel_uos_qty   = {}\n'
                     '  cancel_uos_price = {}\n'
                     '\n'.format(cancel_uom, cancel_uom_qty, cancel_uom_price,
                                 cancel_uos, cancel_uos_qty, cancel_uos_price))
        value = {}
        if not context:
            context = {}
        warning = {}
#         if context.get('skip_uom_qty', False):
#             context.update({'skip_uom_qty': False})
#             return {'value': value, 'context': context}
        # We must calculate the price (UoM) BEFORE checking the cancel flag,
        # due to the possibility of using pricelists.
        # This must apply if change was manual or triggered by another onchange
        # Beware of uom used!!
        if product_id:
            product_obj = self.pool.get('product.product')
            prod = product_obj.browse(cr, uid, product_id, context=context)

            product_uom_obj = self.pool.get('product.uom')
            qty_uom_real = product_uom_obj._compute_qty(cr, uid,
                                                        uom_id, qty_uom,
                                                        prod.uom_id.id)
            new_price_unit_uom, pu_uom_warning = self._price_unit_get(
                cr, uid, product_id, uom_id, qty_uom_real, type, partner_id,
                currency_id, context=context)
            logger.debug('\n\n\n\n>>>> onchange_quantity_uom -> '
                         '  New price_unit(1): \n'
                         '    {}\n'
                         '  Old price_unit:'
                         '    {}\n\n\n\n\n'.format(new_price_unit_uom,
                                                   price_unit_uom))
#             result['price_unit'] = price_unit_uom  # might be False
            warning.update(pu_uom_warning)
        else:
            new_price_unit_uom = price_unit_uom

        # Price (UoM)
        diff1 = (new_price_unit_uom != price_unit_uom)
        if diff1:
            cancel_uom_price = diff1 or not product_id
            value.update({'price_unit_uom': new_price_unit_uom})
        # ---------------------------------------------
        if cancel_uom_qty:
            value.update({'cancel_uom_qty': False})
            logger.debug('>>>> onchange_quantity_uom -> Cancelled!')
            return {'value': value, 'context': context, 'warning': warning}
        # ---------------------------------------------
        logger.debug('>>>> onchange_quantity_uom --> passed cancel_uom_qty')
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)

        if not uos_id:
            new_qty_uos = qty_uom
            new_price_unit_uos = new_price_unit_uom
        elif not product_id or not product_has_uos:
            # If not product defined, it is user's responsability
            # If there is no product defined, or it has no defined UoS,
            # but uos_id field exists, we just compute the new quantity
            # May be the case of a uom_id != uos_id, but in the same category
            product_uom_obj = self.pool.get('product.uom')
            new_qty_uos = product_uom_obj._compute_qty(cr, uid,
                                                       uom_id, qty_uom, uos_id)
            new_price_unit_uos = new_price_unit_uom
        else:
            product_uom_obj = self.pool.get('product.uom')
            # _qty_swap_uom_uos already handles:
            # if not product or not product.uos_id or not product.uos_coeff
            new_qty_uos = product_uom_obj._qty_swap_uom_uos(
                cr, uid, product_id, 'uom2uos', uom_id, qty_uom, uos_id)
            new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
                cr, uid, product_id, 'uom2uos',
                uom_id, new_price_unit_uom, uos_id)

        # Quantity (UoS)
        diff2 = (new_qty_uos != qty_uos)
        #
        cancel_uos_qty = diff2 or not product_id or not product_has_uos
        value.update({'cancel_uos_qty': cancel_uos_qty})
        if diff2:
            value.update({'quantity': new_qty_uos})
#             value.update({'quantity_dummy': new_qty_uos})
#         context.update({'skip_uos_qty': diff2})

        # Price unit (UoS)
        # Need to calculate this after calculating UoM new price unit
        # and possible new qty_uos
        diff3 = (new_price_unit_uos != price_unit_uos)
        #
        cancel_uos_price = diff3 or not product_id or not product_has_uos
        value.update({'cancel_uos_price': cancel_uos_price})
        if diff3:
            value.update({'price_unit': new_price_unit_uos})  # This is uos

        return {'value': value, 'context': context}

    def onchange_uom_id(self, cr, uid, ids,
                        product_id=None,
                        qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                        qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                        currency_id=False, product_has_uos=False,
                        cancel_uom=False,
                        cancel_uom_qty=False,
                        cancel_uom_price=False,
                        cancel_uos=False,
                        cancel_uos_qty=False,
                        cancel_uos_price=False,
                        context=None):
        """Updates fields derived from a change in uom in form."""
        value = {}
        if not context:
            context = {}
        # ---------------------------------------------
        if cancel_uom:
            value.update({'cancel_uom': False})
            return {'value': value, 'context': context}
        # ---------------------------------------------

        # If not product defined, it is user's responsibility
        if not product_id or not product_has_uos:
            # We will update only uos_id, without further triggers
            # context.update({'skip_uos': True})
            value.update({
                'cancel_uos_qty': True,
                'cancel_uos_price': True,
                'cancel_uos': True,
                'uos_id': uom_id,
                # 'uos_id_dummy': uom_id
            })
            return {'value': value, 'context': context}

        # NOTE: In invoices, uos_id can be product.uom_id or product.uos_id,
        #       depending on whether comes from a sales order or not (insane!)
        # ----------------------------------
        if not uom_id:
            # We just warn, it is user's responsibility to choose a UoM
            warning = {
                'title': 'Unit of measure not set',
                'message': ('Unit of measure (UoM) must be set.\n'
                            'Calculations based on it were skipped.'),
            }
            return {'value': value, 'context': context, 'warning': warning}

        # So far, product.product has a UoS defined, but in this form
        # uos_id may or maybe not be set.
        if not uos_id:
            # We just warn, it is user's responsibility to choose a UoS
            warning = {
                'title': 'Unit of sale not set',
                'message': ('Unit of sale (UoS) must be set.\n'
                            'Calculations based on it were skipped.'),
            }
            return {'value': value, 'context': context, 'warning': warning}

        # Finally, if all is set correctly (product_id, product_has_uos,
        # uom_id, uos_id), we calculate accordingly quantity(UoS) and
        # price_unit(UoS)

        # NOTE: [1]
        # ---------
        # Is this cast needed?
        # Yes, we need to cast in float because the value received from
        # web client maybe an integer (Javascript and JSON do not
        # make any difference between 3.0 and 3). This cause a problem if
        # you encode, for example, 2 liters at 1.5 per
        # liter => total is computed as 3.0, then trigger an onchange
        # that recomputes price_per_liter as 3/2=1 (instead
        # of 3.0/2=1.5)

        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)
        price_unit_uom = float(price_unit_uom)
        price_unit_uos = float(price_unit_uos)

        # Calculate new quantity and price_unit (UoS) taking into account
        # product.uos_coeff, AND ALSO that the selected UoM or UoS in this
        # form might not be the same as in product.product, but in the same
        # product-uom.categ (so a unit factor is also applied)
        product_uom_obj = self.pool.get('product.uom')
        # --> Quantity
        new_qty_uos = product_uom_obj._qty_swap_uom_uos(
            cr, uid, product_id, 'uom2uos', uom_id, qty_uom, uos_id)
        diff1 = (new_qty_uos != qty_uos)
        cancel_uos_qty = diff1 or not product_id or not product_has_uos
        value.update({'cancel_uos_qty': cancel_uos_qty})
        if diff1:
            value.update({'quantity': new_qty_uos})  # This is uos
#             value.update({'quantity_dummy': new_qty_uos})  # This is uos
#         context.update({'skip_uos_qty': diff1})

        # --> Price_unit
        new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
            cr, uid, product_id, 'uom2uos', uom_id, price_unit_uom, uos_id)
        diff2 = (new_price_unit_uos != price_unit_uos)
        cancel_uos_price = diff2 or not product_id or not product_has_uos
        value.update({'cancel_uos_price': cancel_uos_price})
        if diff2:
            value.update({'price_unit': new_price_unit_uos})  # This is uos
#             value.update({'price_unit_dummy': new_price_unit_uos})  # uos
#         context.update({'skip_uos_price': diff2})
        return {'value': value, 'context': context}

    def onchange_price_unit_uom(self, cr, uid, ids,
                                product_id=None,
                                qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                                qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                                currency_id=False, product_has_uos=False,
                                cancel_uom=False,
                                cancel_uom_qty=False,
                                cancel_uom_price=False,
                                cancel_uos=False,
                                cancel_uos_qty=False,
                                cancel_uos_price=False,
                                context=None):
        """Updates product price_unit (uos)"""
        logger = logging.getLogger(__name__)
        logger.debug('\n'
                     'onchange_price_unit_uom:\n'
                     '  cancel_uom       = {}\n'
                     '  cancel_uom_qty   = {}\n'
                     '  cancel_uom_price = {}\n'
                     '  cancel_uos       = {}\n'
                     '  cancel_uos_qty   = {}\n'
                     '  cancel_uos_price = {}\n'
                     '\n'.format(cancel_uom, cancel_uom_qty, cancel_uom_price,
                                 cancel_uos, cancel_uos_qty, cancel_uos_price))
        value = {}
        if not context:
            context = {}
#         if context.get('skip_uom_price', False):
#             context.update({'skip_uom_price': False})
#             return {'value': value, 'context': context}
        # ---------------------------------------------
        if cancel_uom_price:
            value.update({'cancel_uom_price': False})
            logger.debug('>>>> onchange_price_unit_uom -> Cancelled!')
            return {'value': value, 'context': context}
        # ---------------------------------------------
        # Cast needed. See NOTE: [1]
        price_unit_uom = float(price_unit_uom)
        price_unit_uos = float(price_unit_uos)
        # _compute_qty(self, cr, uid, from_uom_id, qty, to_uom_id=False):
        # _compute_price(self, cr, uid, from_uom_id, price, to_uom_id=False):
        if not uos_id:
            new_price_unit_uos = price_unit_uom
        elif not product_id or not product_has_uos:
            # If there is no product defined, or it has no defined UoS,
            # but uos_id field exists, we just compute the new price
            # Maybe  the case of a uom_id != uos_id, but in the same category
            product_uom_obj = self.pool.get('product.uom')
            new_price_unit_uos = product_uom_obj._compute_price(
                cr, uid, uom_id, price_unit_uom, uos_id)
        else:
            product_uom_obj = self.pool.get('product.uom')
            new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
                cr, uid, product_id, 'uom2uos', uom_id, price_unit_uom, uos_id)
        logger.debug(('>>>> onchange_price_unit_uom -> \n'
                      '     price_unit_uos    :{}'
                      '     new_price_unit_uos:{}').format(price_unit_uos,
                                                           new_price_unit_uos))
        diff1 = (new_price_unit_uos != price_unit_uos)
        value.update({'cancel_uos_price': diff1 or not product_has_uos})
        if diff1:
            value.update({'price_unit': new_price_unit_uos})
#             value.update({'price_unit_dummy': new_price_unit_uos})
#         context.update({'skip_uos_price': diff1})
        return {'value': value, 'context': context}

    # ---- UoS
    def onchange_quantity(self, cr, uid, ids,
                          product_id=None,
                          qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                          qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                          currency_id=False,  product_has_uos=False,
                          cancel_uom=False,
                          cancel_uom_qty=False,
                          cancel_uom_price=False,
                          cancel_uos=False,
                          cancel_uos_qty=False,
                          cancel_uos_price=False,
                          context=None):
        """Updates quantity_uom in form."""
        logger = logging.getLogger(__name__)
        logger.debug('\n'
                     'onchange_quantity:\n'
                     '  cancel_uom       = {}\n'
                     '  cancel_uom_qty   = {}\n'
                     '  cancel_uom_price = {}\n'
                     '  cancel_uos       = {}\n'
                     '  cancel_uos_qty   = {}\n'
                     '  cancel_uos_price = {}\n'
                     '\n'.format(cancel_uom, cancel_uom_qty, cancel_uom_price,
                                 cancel_uos, cancel_uos_qty, cancel_uos_price))
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)

        value = {}
        value.update({'quantity_dummy': qty_uos})
        if not context:
            context = {}
#         if context.get('skip_uos_qty', False):
#             context.update({'skip_uos_qty': False})
#             return {'value': value, 'context': context}
        # ---------------------------------------------
        if cancel_uos_qty:
            value.update({'cancel_uos_qty': not product_has_uos})
            logger.debug('>>>> onchange_quantity -> Cancelled!')
            return {'value': value, 'context': context}
        # ---------------------------------------------
        # If not product defined, it is user's responsibility
        if not product_id:
            return {'value': value, 'context': context}

        product_uom_obj = self.pool.get('product.uom')
        # _qty_swap_uom_uos already handles:
        # if not product or not product.uos_id or not product.uos_coeff
        new_qty_uom = product_uom_obj._qty_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, qty_uos, uom_id)
        diff1 = (new_qty_uom != qty_uom)
        value.update({'cancel_uom_qty': diff1 or not product_has_uos})
        if diff1:
            value.update({'quantity_uom': new_qty_uom})
#         context.update({'skip_uom_qty': diff1})
        return {'value': value, 'context': context}

    def onchange_uos_id(self, cr, uid, ids, product_id,
                        qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                        qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                        name='', type='out_invoice', partner_id=False,
                        fposition_id=False,
                        address_invoice_id=False, currency_id=False,
                        product_has_uos=False,
                        cancel_uom=False,
                        cancel_uom_qty=False,
                        cancel_uom_price=False,
                        cancel_uos=False,
                        cancel_uos_qty=False,
                        cancel_uos_price=False,
                        context=None, company_id=None):
        """Updates fields derived from a change in uos in form."""
        logger = logging.getLogger(__name__)
        logger.debug('\n'
                     'onchange_uos_id:\n'
                     '----------------\n'
                     '  uom_id           = {}\n'
                     '  uos_id           = {}\n'
                     '  product_has_uos  = {}\n'
                     '  cancel_uom       = {}\n'
                     '  cancel_uom_qty   = {}\n'
                     '  cancel_uom_price = {}\n'
                     '  cancel_uos       = {}\n'
                     '  cancel_uos_qty   = {}\n'
                     '  cancel_uos_price = {}\n'
                     '\n'.format(uom_id, uos_id, product_has_uos,
                                 cancel_uom, cancel_uom_qty, cancel_uom_price,
                                 cancel_uos, cancel_uos_qty, cancel_uos_price))
        value = {}
        if not context:
            context = {}
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)
        price_unit_uom = float(price_unit_uom)
        price_unit_uos = float(price_unit_uos)

        if company_id is None:
            company_id = context.get('company_id', False)
        else:
            company_id = company_id
        context = dict(context)
        context.update({'company_id': company_id})
        # We call super() for compatibility
        res = super(account_invoice_line,
                    self).uos_id_change(cr, uid, ids,
                                        product_id, uos_id, qty_uos, name,
                                        type, partner_id, fposition_id,
                                        price_unit_uos, address_invoice_id,
                                        currency_id, context=context)
                                        # , company_id)
#         value = dict(res['value'])
        logger.debug('>>>> onchange_uos_id -> value(0): {}'.format(value))

        # Update the uos_id_dummy field, for if uos_id is invisible
        value.update({'uos_id_dummy': uos_id})
        if cancel_uos:
            cancel_uos = not product_id or not product_has_uos
            value.update({'cancel_uos': cancel_uos})  # False})
            logger.debug('>>>> onchange_uos_id -> Cancelled!')
            logger.debug('>>>> onchange_uos_id -> value(1): {}'.format(value))
            return {'value': value, 'context': context}
        logger.debug('>>>> onchange_uos_id -> NOT Cancelled!!!!!!!!!!!!!')
        logger.debug('>>>> onchange_uos_id -> value(2): {}'.format(value))
        # If not product defined, it is user's responsibility
        if not product_id or not product_has_uos:
            # We will update only uom_id, without further triggers
            value.update({
                'cancel_uos': True,
                'cancel_uos_qty': True,
                'cancel_uom_price': True,
                'cancel_uom': True,
                'uom_id': uos_id,
            })
            logger.debug('\n\n >>>> onchange_uos_id -> value(3): {}'
                         '\n\n'.format(value))
            return {'value': value, 'context': context}
        else:
            value.update({
                'cancel_uos': False,
                'cancel_uos_qty': False,
                'cancel_uom_price': False,
            })
        # NOTE: In invoices, uos_id can be product.uom_id or product.uos_id,
        #       depending on whether comes from a sales order or not (insane!)
        # ----------------------------------
        # So far, product.product has a UoS defined, but in this form
        # uos_id may or maybe not be set.
        if not uos_id:
            # We just warn, it is user's responsibility to choose a UoS
            warning = {
                'title': _('Unit of sale not set'),
                'message': _('Unit of sale (UoS) must be set.\n'
                             'Calculations based on it were skipped.'),
            }
            return {'value': value, 'context': context, 'warning': warning}

        if not uom_id:
            # We just warn, it is user's responsibility to choose a UoM
            warning = {
                'title': _('Unit of measure not set'),
                'message': _('Unit of measure (UoM) must be set.\n'
                             'Calculations based on it were skipped.'),
            }
            return {'value': value, 'context': context, 'warning': warning}

        # Finally, if all is set correctly (product_id, product_has_uos,
        # uom_id, uos_id), we calculate accordingly quantity(UoS) and
        # price_unit(UoS)

        # Calculate new quantity_uom and price_unit_uom (UoM) accordingly to
        # product.uos_coeff, AND ALSO that the selected UoM or UoS in this
        # form might not be the same as in product.product, but in the same
        # product-uom.categ (so a unit factor is also applied)
        product_uom_obj = self.pool.get('product.uom')
        # --> Quantity
        new_qty_uom = product_uom_obj._qty_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, qty_uos, uom_id)
        diff1 = (new_qty_uom != qty_uom)
        value.update({'cancel_uom_qty': False})  # diff1}) NOTE: Needed?
        if diff1:
            value.update({'quantity_uom': new_qty_uom})  # This is uom
#         context.update({'skip_uom_qty': diff1})  # Skip trigger back?

        # --> Price_unit
        new_price_unit_uom = product_uom_obj._price_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, price_unit_uos, uom_id)
        diff2 = (new_price_unit_uom != price_unit_uom)
        value.update({'cancel_uom_price': diff2})
        if diff2:
            value.update({'price_unit_uom': new_price_unit_uom})  # This is uom
#         context.update({'skip_uom_price': diff2})  # Skip trigger back?
        return {'value': value, 'context': context}

    def onchange_price_unit(self, cr, uid, ids,
                            product_id=None,
                            qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                            qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                            currency_id=False,
                            product_has_uos=False,
                            cancel_uom=False,
                            cancel_uom_qty=False,
                            cancel_uom_price=False,
                            cancel_uos=False,
                            cancel_uos_qty=False,
                            cancel_uos_price=False,
                            context=None):
        """Updates product price_unit_uom"""
        logger = logging.getLogger(__name__)
        logger.debug('\n'
                     'onchange_price_unit:\n'
                     '  uom_id       = {}\n'
                     '  uos_id       = {}\n'
                     '  cancel_uom       = {}\n'
                     '  cancel_uom_qty   = {}\n'
                     '  cancel_uom_price = {}\n'
                     '  cancel_uos       = {}\n'
                     '  cancel_uos_qty   = {}\n'
                     '  cancel_uos_price = {}\n'
                     '\n'.format(uom_id, uos_id,
                                 cancel_uom, cancel_uom_qty, cancel_uom_price,
                                 cancel_uos, cancel_uos_qty, cancel_uos_price))
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)
        price_unit_uom = float(price_unit_uom)
        price_unit_uos = float(price_unit_uos)

        value = {}
        value.update({'price_unit_dummy': price_unit_uos})
        if not context:
            context = {}
        # ---------------------------------------------
        if cancel_uos_price:
            cancel_uos_price = not product_id or not product_has_uos
            value.update({'cancel_uos_price': cancel_uos_price})  # False})
            logger.debug('>>>> onchange_price_unit -> Cancelled!')
            return {'value': value, 'context': context}
        # ---------------------------------------------

        logger.debug('>>>> onchange_price_unit ---> Passed skip_uos_price')
        product_uom_obj = self.pool.get('product.uom')
        new_price_unit_uom = product_uom_obj._price_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, price_unit_uos, uom_id)

        diff1 = (new_price_unit_uom != price_unit_uom)
        value.update({'cancel_uom_price': diff1 or not product_has_uos})
        if diff1:
            value.update({'price_unit_uom': new_price_unit_uom})
#         context.update({'skip_uom_price': diff1})
        logger.debug('\n\n>>>> onchange_price_unit ---> value:{}'
                     '\n'.format(value))
        return {'value': value, 'context': context}

account_invoice_line()


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None,
               journal_id=None):

        invoices = self.read(cr, uid, ids,
                             ['name', 'type', 'number', 'reference', 'comment',
                              'date_due', 'partner_id', 'address_contact_id',
                              'address_invoice_id', 'partner_contact',
                              'partner_insite', 'partner_ref', 'payment_term',
                              'account_id', 'currency_id', 'invoice_line',
                              'tax_line', 'journal_id', 'user_id',
                              'fiscal_position'])

        obj_invoice_line = self.pool.get('account.invoice.line')
        obj_invoice_tax = self.pool.get('account.invoice.tax')
        obj_journal = self.pool.get('account.journal')
        new_ids = []
        for invoice in invoices:
            del invoice['id']

            type_dict = {
                'out_invoice': 'out_refund',  # Customer Invoice
                'in_invoice': 'in_refund',  # Supplier Invoice
                'out_refund': 'out_invoice',  # Customer Refund
                'in_refund': 'in_invoice',  # Supplier Refund
            }

            invoice_lines = obj_invoice_line.read(cr, uid,
                                                  invoice['invoice_line'])
            invoice_lines = self._refund_cleanup_lines(cr, uid, invoice_lines)

            tax_lines = obj_invoice_tax.read(cr, uid, invoice['tax_line'])
            tax_lines = filter(lambda l: l['manual'], tax_lines)
            tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines)
            if journal_id:
                refund_journal_ids = [journal_id]
            elif invoice['type'] == 'in_invoice':
                refund_journal_ids = obj_journal.search(
                    cr, uid, [('type', '=', 'purchase_refund')])
            else:
                refund_journal_ids = obj_journal.search(
                    cr, uid, [('type', '=', 'sale_refund')])

            if not date:
                date = time.strftime('%Y-%m-%d')
            invoice.update({
                'type': type_dict[invoice['type']],
                'date_invoice': date,
                'state': 'draft',
                'number': False,
                'invoice_line': invoice_lines,
                'tax_line': tax_lines,
                'journal_id': refund_journal_ids
            })

            if period_id:
                invoice.update({
                    'period_id': period_id,
                })

            if description:
                invoice.update({
                    'name': description,
                })

            # take the id part of the tuple returned for many2one fields
            for field in ('address_contact_id', 'address_invoice_id',
                          'partner_id', 'account_id', 'currency_id',
                          'payment_term', 'journal_id', 'user_id',
                          'fiscal_position'):
                invoice[field] = invoice[field] and invoice[field][0]

            for inv_line_tuple in invoice.get('invoice_line', []):
                for tuple_pos in inv_line_tuple:
                    if isinstance(tuple_pos, dict) and tuple_pos.get('uom_id',
                                                                     False):
                        tuple_pos.update({
                            'uom_id': (tuple_pos['uom_id'] and
                                       tuple_pos['uom_id'][0]),
                        })
            # create the new invoice
            new_ids.append(self.create(cr, uid, invoice))

        return new_ids

account_invoice()
