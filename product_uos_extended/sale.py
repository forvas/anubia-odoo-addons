# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import decimal_precision as dp
import logging
# from osv import fields, osv
from openerp.osv import fields, orm
from tools.translate import _
from tools import float_compare


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        return super(sale_order, self)._amount_all(cr, uid, ids, field_name,
                                                   arg, context=context)
#         cur_obj = self.pool.get('res.currency')
#         res = {}
#         for order in self.browse(cr, uid, ids, context=context):
#             res[order.id] = {
#                 'amount_untaxed': 0.0,
#                 'amount_tax': 0.0,
#                 'amount_total': 0.0,
#             }
#             val = val1 = 0.0
#             cur = order.pricelist_id.currency_id
#             for line in order.order_line:
#                 val1 += line.price_subtotal
#                 val += self._amount_line_tax(cr, uid, line, context=context)
#             res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
#             res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
#             res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
#         return res

    def _get_order(self, cr, uid, ids, context=None):
#         keys = super(sale_order, self)._get_order(cr, uid, ids, context)
#         return keys
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids,
                                                            context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(
            _amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 10),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty'],
                                    10),
            },
            multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(
            _amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Taxes',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 10),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty'],
                                    10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(
            _amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Total',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 10),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty'],
                                    10),
            },
            multi='sums',
            help="The total amount."),
    }

sale_order()

class sale_order_line(orm.Model):
    """
Inherit sale_order_line to allow users to enter
price_unit_uos or price_unit (uom) and calculate the other values accordingly.
"""
    _inherit = "sale.order.line"

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        super(sale_order_line, self)._amount_line(cr, uid, ids,
                                                         field_name, arg,
                                                         context=context)
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
         
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_uos:
                base_price = line.price_unit_uos
                qty = line.product_uos_qty
            else:
                base_price = line.price_unit
                qty = line.product_uom_qty
            price = base_price * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, qty,
                                        line.order_id.partner_invoice_id.id,
                                        line.product_id,
                                        line.order_id.partner_id,
                                        context=context)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
            # Customer do not want lines to limit to 'Account' dec. precision 
            res[line.id] = taxes['total']
        return res
        
#
#     def _get_uom_id(self, cr, uid, *args):
#         try:
#             proxy = self.pool.get('ir.model.data')
#             result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
#             return result[1]
#         except Exception, ex:
#             return False

    def _get_uos_id(self, cr, uid, *args):
        logger = logging.getLogger(__name__)
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product',
                                                'product_uos_unit')
            logger.debug('>>>> _get_uos_id > result1: {}'.format(result))
            return result[1]
        except Exception, ex:
            try:
                proxy = self.pool.get('ir.model.data')
                result = proxy.get_object_reference(cr, uid, 'product',
                                                    'product_uom_unit')
                logger.debug('>>>> _get_uos_id > result2: {}'.format(result))
                return result[1]
            except Exception, ex:
                logger.debug('>>>> _get_uos_id > Exception, return False')
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
        'product_has_uos': fields.boolean(
            'Product has UoS defined',
            help=("Checked if selected product has a defined UoS "
                  "(Unit of Sale).")),
        'price_unit_uos': fields.float(
            'Unit Price (UoS)',
            required=True,
            digits_compute=dp.get_precision('Sale Price'),
            states={'draft': [('readonly', False)]}),
        'price_subtotal': fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),
        'product_uos_dummy': fields.related(
            'product_uos', type="many2one", relation="product.uom",
            readonly=True, store=False, string='Product UoS'), 
        'product_uos_qty_dummy': fields.related(
            'product_uos_qty', type="float",
            readonly=True, store=False, string='Quantity (UoS)',
            digits_compute=dp.get_precision('Product UoS')),
        'price_unit_uos_dummy': fields.related(
            'price_unit_uos', type="float",
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
        #    processing of this onchange is skipped, the flag reset to False
        #    (thus 
    }
    _defaults = {
        'product_uom_qty': 1.0,
        'product_uos_qty': 1.0,
        'cancel_uom': False,
        'cancel_uom_qty': False,
        'cancel_uom_price': False,
        'cancel_uos': True,
        'cancel_uos_qty': True,
        'cancel_uos_price': True,
        'product_has_uos': _has_uos,
        'price_unit': 0.0,
        'price_unit_uos': 0.0,
        'product_uos' : _get_uos_id,
        'product_uos_dummy' : _get_uos_id,
    }

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False,
                                         context=None):
        """Prepare the dict of values to create the new invoice line for a
           sale order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        super(sale_order_line,
              self)._prepare_order_line_invoice_line(cr, uid, line, account_id,
                                                     context=context)

        def _get_line_qty(line):
            is_order = (line.order_id.invoice_quantity == 'order')
            if is_order or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('procurement.order').quantity_get(
                    cr, uid, line.procurement_id.id, context=context)

        def _get_line_uom(line):
            is_order = (line.order_id.invoice_quantity == 'order')
            if is_order or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('procurement.order').uom_get(
                    cr, uid, line.procurement_id.id, context=context)

        def _get_line_price_unit_uos(line):
            is_order = (line.order_id.invoice_quantity == 'order')
            if is_order or not line.procurement_id:
                if line.product_uos:
                    return line.price_unit_uos
            return line.price_unit

        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.product_tmpl_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error !'),
                                             _('There is no income account '
                                               'defined for this product:'
                                               ' "%s" (id:%d)') %
                                             (line.product_id.name,
                                              line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(
                        cr, uid, 'property_account_income_categ',
                        'product.category', context=context)
                    account_id = prop and prop.id or False
            uosqty = _get_line_qty(line)
            uos_id = _get_line_uom(line)
            pu = 0.0
            if uosqty:
                pu = _get_line_price_unit_uos(line)
                #pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        #self.pool.get('decimal.precision').precision_get(cr,
                                # uid, 'Sale Price'))
            fpos = line.order_id.fiscal_position or False
            fpos_obj = self.pool.get('account.fiscal.position')
            account_id = fpos_obj.map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error !'),
                                     _('There is no income category account '
                                       'defined in default Properties for '
                                       'Product Category or Fiscal Position '
                                       'is not defined !'))
            res = {
                'name': line.name,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'product_has_uos': line and line.product_id and \
                    line.product_id.uos_id and True or False,
                'product_id': line and line.product_id and \
                    line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'note': line.notes,
                'account_analytic_id': (line.order_id.project_id and
                                        line.order_id.project_id.id or
                                        False),
                'quantity_uom': line.product_uom_qty,
                'uom_id': line.product_uom and line.product_uom.id,
                'price_unit_uom': line.price_unit,
            }
            return res
        return False

    def _get_price_unit(self, cr, uid, ids, pricelist, product,
                        qty=0, uom=False, partner_id=False, date_order=False,
                        context=None):
        value = {}
        warning = {}
        warning_msgs = ''
        qty = float(qty)
        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer '
                         'in the sales form !\n'
                         'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(
                cr, uid, [pricelist], product, qty or 1.0, partner_id,
                dict(context, uom=uom, date=date_order))[pricelist]
            if price is False:
                warn_msg = _("Couldn't find a pricelist line matching this "
                             "product and quantity.\n"
                             "You have to change either the product, the "
                             "quantity or the pricelist.")

                warning_msgs += (_("No valid pricelist line found ! :") + 
                                 warn_msg + "\n\n")
#             else:
#                 value.update({'price_unit': price})
        if warning_msgs:
            warning = {
                'title': _('Configuration Error !'),
                'message' : warning_msgs,
            }
        return price, warning

    def product_id_change(self, cr, uid, ids, pricelist, product,
                          qty_uom=0, uom=False, price_unit_uom=False,
                          qty_uos=0, uos=False, price_unit_uos=False,
                          name='', partner_id=False, lang=False,
                          update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        '''Detects if product has UoS, or if there is no product'''
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty_uom, uom, qty_uos, uos,
            name, partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context=context)
        value = {}
        if not context:
            context = {}
        warning = {}
        warning_msgs = ''
        # Will reset quantity_uom to 1.0 as a initial value
        res['value'].update({'product_uom_qty': 1.0,})
        if not product:
            res['domain'].update({'product_uom': [('category_id', '!=', '')],
                                  'product_uos': [('category_id', '!=', '')],
                                  })
            res['value'].update({'product_has_uos': False,
                                 'uos': False,
                                 'uom': False,
                                 'price_unit': 0.0,
                                 'price_unit_uos': 0.0,
                                 })
            return res

        # If there is a product defined:
        product_obj = self.pool.get('product.product')
        prod = product_obj.browse(cr, uid, product, context=context)

        new_uom_id = prod.uom_id and prod.uom_id.id or False
        new_uos_id = prod.uos_id and prod.uos_id.id or new_uom_id
        product_has_uos = prod.uos_id and True or False

        res['value'].update({'product_uom': new_uom_id,
                             'product_has_uos': product_has_uos,
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
        # Check packaging
        pac_res = self.product_packaging_change(cr, uid, ids, pricelist,
                                                product, qty_uom_real,
                                                prod.uom_id.id,
                                                partner_id, packaging,
                                                context=context)
        pac_value = pac_res.get('value', {})
        pac_packaging = pac_value.get('product_packaging', packaging)
        res['value'].update({'product_packaging': pac_packaging})
        warning_msgs = pac_res.get('warning') and \
            pac_res['warning']['message'] or ''

        # Check availability
        compare_qty = float_compare(prod.virtual_available,
                                    qty_uom_real,
                                    precision_rounding=prod.uom_id.rounding)
        if (prod.type=='product') and int(compare_qty) == -1 and \
                (prod.procure_method=='make_to_stock'):
            warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s '
                         'available !\nThe real stock is %.2f %s. '
                         '(without reservations)') % \
                         (qty_uom_real, prod.uom_id.name,
                          max(0, prod.virtual_available), prod.uom_id.name,
                          max(0, prod.qty_available), prod.uom_id.name)
            warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"

        # Get default price
        new_price_unit_uom, pu_uom_warning = self._get_price_unit(
            cr, uid, ids, pricelist, product, qty=new_qty_uom, uom=uom,
            partner_id=partner_id, date_order=date_order, context=context)
        
#         new_price_unit_uom, pu_uom_warning = self._price_unit_get(
#             cr, uid, product, new_uom_id, qty_uom_real, type, partner_id,
#             currency_id, context=context)

        new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
                cr, uid, product, 'uom2uos',
                new_uom_id, new_price_unit_uom, new_uos_id)
        
        warning.update(pu_uom_warning)
        res['value'].update({'product_uom': new_uom_id,
                             'product_uos': new_uos_id,
                             'product_uom_qty': new_qty_uom,
                             'product_uos_qty': new_qty_uos,
                             'price_unit': new_price_unit_uom,
                             'price_unit_uos': new_price_unit_uos,
                             })

        # Due to the complexity of chained changes involved, it is easier
        # to avoid them completely and update all needed changes in this
        # function only
        # NOTE: Cannot force it to True because if value doesn't change
        #       the flag will affect next change, uncontrollably
        cancels = {
             'cancel_uom': (new_uom_id != uom),
             'cancel_uom_qty': (new_qty_uom != qty_uom),
             'cancel_uom_price': (new_price_unit_uom != price_unit_uom),
             'cancel_uos': (new_uos_id != uos),
             'cancel_uos_qty': (new_qty_uos != qty_uos),
             'cancel_uos_price': (new_price_unit_uos != price_unit_uos),
             }
        # Looks like order matters
        value.update(cancels)
        value.update(res.get('value', {}))
        
        # Restrain the UoM drop menu to the its category
        prod_uom_cat = prod.uom_id and prod.uom_id.category_id.id or False
        if prod_uom_cat:
            res['domain'].update({
                'product_uom': [('category_id','=',prod_uom_cat)]
            })
        else:
            res['domain'].update({'product_uom': [('category_id','!=',False)]})
        # Restrain the UoS drop menu to the its category
        prod_uos_cat = prod.uos_id and prod.uos_id.category_id.id or \
            prod_uom_cat

        if prod_uos_cat:
            res['domain'].update({
                'product_uos': [('category_id','=',prod_uos_cat)]
            })
        else:
            res['domain'].update({'product_uos': [('category_id','!=',False)]})
        
        return {'value': value,
                'domain': res.get('domain', {}),
                'warning': res.get('warning', {}),
                'context': context,
                }
#         
#         uom_category_id = product.uom_id.category_id.id
#         # Restrain the UoM drop menu to the its category
#         res['domain'].update({
#             'product_uom': [('category_id', '=', uom_category_id)]})
#         if product.uos_id:
#             res['value'].update({'product_has_uos': True})
#             uos_category_id = product.uos_id.category_id.id
#             # Restrain the UoS drop menu to the its category
#             res['domain'].update({
#                 'product_uos': [('category_id', '=', uos_category_id)]})
#         else:
#             res['value'].update({'product_has_uos': False})
#             # Set the UoS = UoM 
#             res['value'].update({'product_uos': product.uom_id.id})
#             res['value'].update({'product_uos_dummy': product.uom_id.id})
#             # Set UoS domain = UoM domain
#             res['domain'].update({
#                 'product_uos': [('category_id', '=', uom_category_id)]})
# 
#         return res

    # ---- UoM
    def onchange_product_uom_qty(self, cr, uid, ids,
                                 pricelist, product_id=None, 
                                 qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                                 qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                                 product_has_uos=False,
                                 cancel_uom=False,
                                 cancel_uom_qty=False, cancel_uom_price=False,
                                 cancel_uos=False,
                                 cancel_uos_qty=False, cancel_uos_price=False,
                                 partner_id=False, lang=False,
                                 update_tax=False, date_order=False,
                                 packaging=False, fiscal_position=False,
                                 flag=False, context=None):
        """Updates product_uos_qty, and th_weight."""
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty=qty_uom,
            uom=uom_id, qty_uos=qty_uos, uos=uos_id, name='',
            partner_id=partner_id, lang=False, update_tax=False,
            date_order=date_order, packaging=packaging,
            fiscal_position=False, flag=False, context=context)
        logger = logging.getLogger(__name__)
        logger.debug('>>>> onchange_product_uom_qty -> context: '
                     '{}'.format(context))
        logger.debug('###################################################\n\n'
                     '>>>> onchange_product_uom_qty :\n'
                     '     partner_id: {}'.format(partner_id))
        value = {}
        if not context:
            context = {}
        warning = {}
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)
        # We must calculate the price (UoM) BEFORE checking the cancel flag,
        # due to the possibility of using pricelists.
        # Also recalculate weight
        # Also check packaging
        # This must apply if change was manual or triggered by another onchange
        # Beware of uom used!!
        if product_id:
            product_obj = self.pool.get('product.product')
            prod = product_obj.browse(cr, uid, product_id, context=context)
            
            product_uom_obj = self.pool.get('product.uom')            
            qty_uom_real = product_uom_obj._compute_qty(cr, uid,
                                                        uom_id, qty_uom,
                                                        prod.uom_id.id)
            # Get default price
            new_price_unit_uom, pu_uom_warning = self._get_price_unit(
                cr, uid, ids, pricelist, product_id, qty=qty_uom, uom=uom_id,
                partner_id=partner_id, date_order=date_order, context=context)
            
#             new_price_unit_uom, pu_uom_warning = self._price_unit_get(
#                 cr, uid, product_id, uom_id, qty_uom_real, type, partner_id,
#                 currency_id, context=context)

            # With quantity in product default uom, recalculate total weight
            th_weight = qty_uom_real * prod.weight
            value.update({'th_weight': th_weight})
            # Check packaging
            res = self.product_packaging_change(cr, uid, ids, pricelist,
                                                product=product_id,
                                                qty=qty_uom_real,
                                                uom=prod.uom_id.id,
                                                partner_id=partner_id,
                                                packaging=packaging,
                                                context=context)
            result = res.get('value', {})
            warning_msgs = res.get('warning') and res['warning']['message'] or ''
        
            
            logger.debug('\n\n\n\n>>>> onchange_quantity_uom -> '
                         '  New price_unit(1): \n'
                         '    {}\n'
                         '  Old price_unit:'
                         '    {}\n\n\n\n\n'.format(new_price_unit_uom,
                                                   price_unit_uom))
            warning.update(pu_uom_warning)
        else:
            new_price_unit_uom = price_unit_uom
        
        # Price (UoM)
        diff1 = (new_price_unit_uom != price_unit_uom)
        if diff1:
            cancel_uom_price = diff1 or not product_id
            value.update({'price_unit': new_price_unit_uom})
        # ---------------------------------------------
        if cancel_uom_qty:
            value.update({'cancel_uom_qty': False})
            logger.debug('>>>> onchange_quantity_uom -> Cancelled!')
            return {'value': value, 'context': context, 'warning': warning}
        # ---------------------------------------------
        logger.debug('>>>> onchange_quantity_uom --> passed cancel_uom_qty')

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
            value.update({'product_uos_qty': new_qty_uos})
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
            value.update({'price_unit_uos': new_price_unit_uos})  # This is uos
        logger.debug('\n>>>> onchange_quantity_uom --> \n'
                     'RETURNING: \n'
                     'qty_uom: {} \n'
                     'new_price_unit_uom: {} \n'
                     'new_qty_uos: {} \n'
                     'new_price_unit_uos: {} \n'
                     '\n'.format(qty_uom, new_price_unit_uom,
                                 new_qty_uos, new_price_unit_uos))

        return {'value': value, 'context': context}
#         
#         
#         if context.get('skip_uom_qty', False):
#             context.update({'skip_uom_qty': False})
#             return {'value': value, 'context': context}
#         qty_uom = float(qty_uom)
#         qty_uos = float(qty_uos)
# 
#         if not product_id:
#             if (qty_uom != qty_uos):
#                 value.update({'product_uos_qty': qty_uom})
#             return {'value': value, 'context': context}
# 
#         product_uom_obj = self.pool.get('product.uom')
#         if uos_id:
#             new_qty_uos = product_uom_obj._qty_swap_uom_uos(
#                 cr, uid, product_id, 'uom2uos', uom_id, qty_uom, uos_id)
#         else:
#             new_qty_uos = qty_uom
# 
#         # Calculate the quantity in product logistic units, for total weight
#         product_obj = self.pool.get('product.product')
#         product = product_obj.browse(cr, uid, product_id)
#         def_uom_id = product.uom_id.id
#         def_qty_uom = product_uom_obj._compute_qty(cr, uid,
#                                                    uom_id, qty_uom, def_uom_id)
#         th_weight = def_qty_uom * product.weight
#         value.update({'th_weight': th_weight})
# 
#         diff1 = (new_qty_uos != qty_uos)
#         if diff1:
#             value.update({'product_uos_qty': new_qty_uos})
#             value.update({'product_uos_qty_dummy': new_qty_uos})
#         context.update({'skip_uos_qty': diff1})
#         return {'value': value, 'context': context}

    def onchange_product_uom(self, cr, uid, ids,
                             product_id=None,
                             qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                             qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                             product_has_uos=False,
                             cancel_uom=False,
                             cancel_uom_qty=False,
                             cancel_uom_price=False,
                             cancel_uos=False,
                             cancel_uos_qty=False,
                             cancel_uos_price=False,
                             context=None):
        """Updates product_uos_qty and price_unit_uos.
        Does not update th_weight."""
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
            # We will update only product_uos, without further triggers
            value.update({
                'cancel_uos_qty': True,
                'cancel_uos_price': True,
                'cancel_uos': True,
                'product_uos': uom_id,
            })
            return {'value': value, 'context': context}
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
        # product_uom.categ (so a unit factor is also applied)
        product_uom_obj = self.pool.get('product.uom')
        # --> Quantity
        new_qty_uos = product_uom_obj._qty_swap_uom_uos(
            cr, uid, product_id, 'uom2uos', uom_id, qty_uom, uos_id)
        diff1 = (new_qty_uos != qty_uos)
        cancel_uos_qty = diff1 or not product_id or not product_has_uos
        value.update({'cancel_uos_qty': cancel_uos_qty})
        if diff1:
            value.update({'product_uom_qty': new_qty_uos})  # This is uos

        # --> Price_unit
        new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
            cr, uid, product_id, 'uom2uos', uom_id, price_unit_uom, uos_id)
        diff2 = (new_price_unit_uos != price_unit_uos)
        cancel_uos_price = diff2 or not product_id or not product_has_uos
        value.update({'cancel_uos_price': cancel_uos_price})
        if diff2:
            value.update({'price_unit_uos': new_price_unit_uos})  # This is uos
        return {'value': value, 'context': context}


#         qty_uom = float(qty_uom)
#         qty_uos = float(qty_uos)
#         
#         if not product_id or not product_has_uos or not uos_id:
#             value.update({'product_uos': uom_id})
#             value.update({'product_uos_dummy': uom_id})
#             new_qty_uos = qty_uom
#             new_price_unit_uos = price_unit_uom
#         else:
#             product_uom_obj = self.pool.get('product.uom')
#             new_qty_uos = product_uom_obj._qty_swap_uom_uos(
#                 cr, uid, product_id, 'uom2uos', uom_id, qty_uom, uos_id)
#             new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
#                 cr, uid, product_id, 'uom2uos', uom_id, price_unit_uom, uos_id)
# 
#         diff1 = (new_qty_uos != qty_uos)
#         if diff1:
#             value.update({'product_uos_qty': new_qty_uos})
#         context.update({'skip_uos_qty': diff1})
# 
#         diff2 = (new_price_unit_uos != price_unit_uos)
#         if diff2:
#             value.update({'price_unit_uos': new_price_unit_uos})
#         context.update({'skip_uos_price': diff2})
#         return {'value': value, 'context': context}

    def onchange_price_unit_uom(self, cr, uid, ids,
                                product_id=None,
                                qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                                qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                                product_has_uos=False,
                                cancel_uom=False,
                                cancel_uom_qty=False,
                                cancel_uom_price=False,
                                cancel_uos=False,
                                cancel_uos_qty=False,
                                cancel_uos_price=False,
                                context=None):
        """Updates product price_unit_uos"""
        value = {}
        if not context:
            context = {}
        # ---------------------------------------------
        if cancel_uom_price:
            value.update({'cancel_uom_price': False})
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
            new_price_unit_uos = product_uom_obj._compute_price(cr, uid,
                                                uom_id, price_unit_uom, uos_id)
        else:
            product_uom_obj = self.pool.get('product.uom')
            new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
                cr, uid, product_id, 'uom2uos', uom_id, price_unit_uom, uos_id)
        diff1 = (new_price_unit_uos != price_unit_uos)
        value.update({'cancel_uos_price': diff1 or not product_has_uos})
        if diff1:
            value.update({'price_unit_uos': new_price_unit_uos})

        logger = logging.getLogger(__name__)
        logger.debug('\n>>>> onchange_price_unit_uom --> \n'
                     'RETURNING: \n'
                     '  qty_uom:            {} \n'
                     '  price_unit_uom:     {} \n'
                     '  qty_uos:            {} \n'
                     '  new_price_unit_uos: {} \n'
                     '\n'.format(qty_uom, price_unit_uom,
                                 qty_uos, new_price_unit_uos))
        return {'value': value, 'context': context}
#     
#         qty_uom = float(qty_uom)
#         qty_uos = float(qty_uos)
# 
#         product_uom_obj = self.pool.get('product.uom')
#         if uos_id:
#             new_price_unit_uos = product_uom_obj._price_swap_uom_uos(
#                 cr, uid, product_id, 'uom2uos', uom_id, price_unit_uom, uos_id)
#         else:
#             new_price_unit_uos = price_unit_uom
#
#         diff1 = (new_price_unit_uos != price_unit_uos)
#         if diff1:
#             value.update({'price_unit_uos': new_price_unit_uos})
#             value.update({'price_unit_uos_dummy': new_price_unit_uos})
#         context.update({'skip_uos_price': diff1})
#         return {'value': value, 'context': context}

    #def uos_change(self, cr, uid, ids,
                   #product_uos, product_uos_qty=0, product_id=None):
    def onchange_product_uos_qty(self, cr, uid, ids,
                                 product_id=None,
                                 qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                                 qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                                 product_has_uos=False,
                                 cancel_uom=False,
                                 cancel_uom_qty=False,
                                 cancel_uom_price=False,
                                 cancel_uos=False,
                                 cancel_uos_qty=False,
                                 cancel_uos_price=False,
                                 context=None):
        """ Updates product_qty_uom or product_qty_uos, and weight """
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)

        value = {}
        value.update({'product_uos_qty_dummy': qty_uos})
        if not context:
            context = {}
#         if context.get('skip_uos_qty', False):
#             context.update({'skip_uos_qty': False})
#             return {'value': value, 'context': context}
        # ---------------------------------------------
        if cancel_uos_qty:
            value.update({'cancel_uos_qty': not product_has_uos})
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
            value.update({'product_uom_qty': new_qty_uom})
#         context.update({'skip_uom_qty': diff1})
        return {'value': value, 'context': context}
#     
#         logger = logging.getLogger(__name__)
#         logger.debug('>>>> onchange_product_uos_qty -> context: {}'.format(context))
#         value = {}
#         value.update({'product_uos_qty_dummy': qty_uos})
#         if not context:
#             context = {}
#         if context.get('skip_uos_qty', False):
#             context.update({'skip_uos_qty': False})
#             return {'value': value, 'context': context}
#         qty_uom = float(qty_uom)
#         qty_uos = float(qty_uos)
# 
#         product_uom_obj = self.pool.get('product.uom')
#         if uos_id:
#             new_qty_uom = product_uom_obj._qty_swap_uom_uos(
#                 cr, uid, product_id, 'uos2uom', uos_id, qty_uos, uom_id)
#         else:
#             new_qty_uom = qty_uos
# 
#         diff1 = (new_qty_uom != qty_uom)
#         if diff1:
#             value.update({'product_uom_qty': new_qty_uom})
#         context.update({'skip_uom_qty': diff1})
#         return {'value': value, 'context': context}

    def onchange_product_uos(self, cr, uid, ids,
                             product_id=None,
                             qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                             qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                             product_has_uos=False,
                             cancel_uom=False,
                             cancel_uom_qty=False,
                             cancel_uom_price=False,
                             cancel_uos=False,
                             cancel_uos_qty=False,
                             cancel_uos_price=False,
                             context=None):
        """Updates product_uom_qty (if uos_id is defined) or
        updates product_uos_qty (if uos_id is not defined)."""
        logger = logging.getLogger(__name__)
        logger.debug('>>>> sale::onchange_product_uos -> context: {}'.format(context))
        value = {}
        if not context:
            context = {}
        # Update the uos_id_dummy field, for if uos_id is invisible
        value.update({'product_uos_dummy': uos_id})
        if cancel_uos:
            cancel_uos = not product_id or not product_has_uos
            value.update({'cancel_uos': cancel_uos})  # False})
            return {'value': value, 'context': context}
        # ---------------------------------------------
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)
        price_unit_uom = float(price_unit_uom)
        price_unit_uos = float(price_unit_uos)

        # If not product defined, it is user's responsibility
        if not product_id or not product_has_uos:
            # We will update only uom_id, without further triggers
            value.update({
                'cancel_uos': True,
                'cancel_uos_qty': True,
                'cancel_uom_price': True,
                'cancel_uom': True,
                'product_uom': uos_id,
            })
            return {'value': value, 'context': context}
        else:
            value.update({
                'cancel_uos': False,
                'cancel_uos_qty': False,
                'cancel_uom_price': False,
            })
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
        # uom_id, uos_id), we calculate accordingly product_uos_qty (UoS) and
        # price_unit_uos (UoS) 

        # Calculate new product_uom_qty and price_unit_uom (UoM) accordingly to
        # product.uos_coeff, AND ALSO that the selected UoM or UoS in this
        # form might not be the same as in product.product, but in the same
        # product-uom.categ (so a unit factor is also applied)
        product_uom_obj = self.pool.get('product.uom')

        # --> Price_unit
        new_price_unit_uom = product_uom_obj._price_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, price_unit_uos, uom_id)
        diff2 = (new_price_unit_uom != price_unit_uom)
        value.update({'cancel_uom_price': diff2})
        if diff2:
            value.update({'price_unit': new_price_unit_uom})  # This is uom

        # --> Quantity
        new_qty_uom = product_uom_obj._qty_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, qty_uos, uom_id)
        
        diff1 = (new_qty_uom != qty_uom)
        logger.debug('\n\n\n---------------------------------------'
                     '>>>> sale::onchange_product_uos -> \n'
                     'qty_uos:     {}\n'
                     'qty_uom:     {}\n'
                     'new_qty_uom: {}\n'
                     'diff1:       {}'
                     '\n\n\n---------------------------------------'
                     ' '.format(qty_uos, qty_uom, new_qty_uom, diff1))
        value.update({'cancel_uom_qty': False})  # diff1}) NOTE: Needed?
        if diff1:
            value.update({'product_uom_qty': new_qty_uom})  # This is uom
#         context.update({'skip_uom_qty': diff1})  # Skip trigger back?

        return {'value': value, 'context': context}

#
#         if not product_id or not uos_id or not product_has_uos:
#             # If uos not defined, we take uom values for qty and price
#             value.update({'product_uos_qty': qty_uom})
#             value.update({'product_uos_qty_dummy': qty_uom})
#             value.update({'price_unit_uos': price_unit_uom})
#             value.update({'price_unit_uos_dummy': price_unit_uom})
#             context.update({'skip_uom_qty': True})
#             context.update({'skip_uom_price': True})
#             return {'value': value, 'context': context}
#
# #         context.update({'skip_uom_qty': False})
# #         context.update({'skip_uom_price': False})
#
#         product_uom_obj = self.pool.get('product.uom')
#         new_qty_uom = product_uom_obj._qty_swap_uom_uos(
#             cr, uid, product_id, 'uos2uom', uos_id, qty_uos, uom_id)
#         new_price_unit_uom = product_uom_obj._price_swap_uom_uos(
#             cr, uid, product_id, 'uos2uom', uos_id, price_unit_uos, uom_id)
#
#         diff1 = (new_qty_uom != qty_uom)
#         if diff1:
#             value.update({'product_uom_qty': new_qty_uom})
#         context.update({'skip_uom_qty': diff1})
#
#         diff2 = (new_price_unit_uom != price_unit_uom)
#         if diff2:
#             value.update({'price_unit': new_price_unit_uom})
#         context.update({'skip_uom_price': diff2})
#         return {'value': value, 'context': context}

    def onchange_price_unit_uos(self, cr, uid, ids,
                                product_id=None,
                                qty_uom=0.0, uom_id=None, price_unit_uom=1.0,
                                qty_uos=0.0, uos_id=None, price_unit_uos=1.0,
                                product_has_uos=False,
                                cancel_uom=False,
                                cancel_uom_qty=False,
                                cancel_uom_price=False,
                                cancel_uos=False,
                                cancel_uos_qty=False,
                                cancel_uos_price=False,
                                context=None):
        """Updates product price_unit"""
        value = {}
        if not context:
            context = {}
        # Cast needed. See NOTE: [1]
        qty_uom = float(qty_uom)
        qty_uos = float(qty_uos)
        price_unit_uom = float(price_unit_uom)
        price_unit_uos = float(price_unit_uos)
        # Update the price_unit_uos_dummy field, for if price_unit_uos is
        # invisible
        value.update({'price_unit_uos_dummy': price_unit_uos})
        # ---------------------------------------------
        if cancel_uos_price:
            cancel_uos_price = not product_id or not product_has_uos
            value.update({'cancel_uos_price': cancel_uos_price})  # False})
            return {'value': value, 'context': context}
        # ---------------------------------------------
        product_uom_obj = self.pool.get('product.uom')
        new_price_unit_uom = product_uom_obj._price_swap_uom_uos(
            cr, uid, product_id, 'uos2uom', uos_id, price_unit_uos, uom_id)

        diff1 = (new_price_unit_uom != price_unit_uom)
        value.update({'cancel_uom_price': diff1 or not product_has_uos})
        if diff1:
            value.update({'price_unit': new_price_unit_uom})  # uom
        return {'value': value, 'context': context}

#         product_uom_obj = self.pool.get('product.uom')
#         new_price_unit_uom = product_uom_obj._price_swap_uom_uos(
#             cr, uid, product_id, 'uos2uom', uos_id, price_unit_uos, uom_id)

#         diff1 = (new_price_unit_uom != price_unit_uom)
#         if diff1:
#             value.update({'price_unit': new_price_unit_uom})
#         context.update({'skip_uos_price': diff1})
#         return {'value': value, 'context': context}

sale_order_line()
