# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Alejandro Santana <alejandrosantana@anubia.es>
#    Copyright (c) All rights reserved:
#        (c) 2013      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    # product_uos_extended
    "name": "Unit of Sale price in product, sales order and invoices",
    "version": "1.1",
    "depends": [
        "account",
        "decimal_precision",
        "product",
        "sale",
    ],
    "author": "Alejandro Santana <alejandrosantana@anubia.es>",
    "category": "Product/Sale/Accounting",
    "description": """
This module aims to provide correct support when using 2 units of measure for
products: UoM (Unit of Measure, the default) and UoS (Unit Of Sale), fixing
and improving the default behaviour.
    * If a 'Unit of Sale' (UoS) is specified for a product, adds the
      possibility to also specify the list price per UoS instead of
      list price per 'Unit of Measure' (UoM).
    * When updating list price (per UoS or per UoM), UoM, UoS or UoScoefficient
      the others will be updated accordingly.
    * This applies for products, sales orders and invoices.
    * In sale orders and invoices, when changing a product, its available
      UoM and UoS (if any) options are filtered by unit category. This fixes
      the weird situation where a unit not matching the product was available.
    * In sale orders and invoices, if a UoM or UoS (if any) is changed within
      its category, the quantities and unit prices are calculated accordingly.
      Also, quantity is checked against price lists correctly handling the
      selected unit (by calculating internally the base UoM defined in the
      product) and computes the correct unit prices matching the new quantity.
    * When invoicing from a sale order, it handles the correct mapping of 
      UoM and UoS data from sale order to invoice.
      This corrects the default 'funnel' behaviour:
      * where UoM (or UoS, if exists) is passed to invoices as UoS data, 
        no matter the product configuration.
      * and avoids loosing info about units (and related quantities and prices) 
        when passing from sales orders to invoices.
""",
    "init_xml": [],
    'update_xml': [
        "account_invoice_view.xml",
        "account_report.xml",
        "product_view.xml",
        "sale_view.xml",
        "stock_view.xml",
#         "report/account_invoice_report_view.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    #'certificate': 'certificate',
}
