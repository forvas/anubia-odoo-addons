# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2014      Anubía, soluciones en la nube,SL (http://www.anubia.es)
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
    "name": "Carrier info in sale orders, invoices and picking lists.",
    "version": "0.1",
    "author": "Alejandro Santana <alejandrosantana@anubia.es>",
    "website": "www.anubia.es",
    "license": "AGPL-3",
    "category": "Generic Modules/Others",
    "description": """
Carrier info module
===================
* Adds carrier/shipment info in sale orders, invoices and picking lists:
    * Carrier
    * Vehicle info (like lorry and trailer plates, ship name,...)
    * Extra info (for whatever needed regarding the carrier).
""",
    "depends": [
        "account",
        "sale",
        "stock",
    ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        "account_invoice_view.xml",
        "partner_view.xml",
        "sale_view.xml",
        "stock_view.xml",
    ],
    "active": False,
    "installable": True
}
