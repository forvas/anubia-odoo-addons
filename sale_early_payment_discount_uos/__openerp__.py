# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2013      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#
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
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################

{
    "name": "Sales early payment discount extension for UoS",
    "description": """
Sale early payment discount extension for UoS
=============================================
    * Extends sale_early_payment_discount to support UoS (Unit of Sale)
      improvements introduced by product_list_price_uos in sale order report.
    * Overrides sales order report.
    * Adds subtle enhancement in views (just a newline to separate data).
""",
    "version": "1.0",
    "author": 'Alejandro Santana <alejandrosantana@anubia.es>',
    "contributors": [],
    "depends": [
        "decimal_precision",
        "product_uos_extended",
        "sale_early_payment_discount",
    ],
    "category": "Sales",
    "init_xml": [],
    "update_xml": ['sale_view.xml',
                   'sale_report.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
