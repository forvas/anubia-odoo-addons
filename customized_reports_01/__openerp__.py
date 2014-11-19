# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2013-2014 Anubía, soluciones en la nube,SL (http://www.anubia.es)
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
    # product_list_price_uos
    "name": "Customized reports for specific customer",
    "version": "1.0",
    "depends": [
        "product_dp_extra",
        "product_uos_extended",
        "purchase_discount",
        "sale_payment",
        "sale_early_payment_discount_uos",
        "carrier_info",
    ],
    "author": "Alejandro Santana <alejandrosantana@anubia.es>",
    "category": "Customization",
    "description": """
This provides customized reports for a specific customer.
""",
    "init_xml": [],
    'update_xml': [
        "account_report.xml",
        "purchase_report.xml",
        "sale_report.xml",
        "stock_report.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    #'certificate': 'certificate',
}
