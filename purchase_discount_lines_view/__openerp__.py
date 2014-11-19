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
    # purchase_discount_lines_view
    "name": "Show purchase discounts in purchase lines tree view",
    "version": "1.0",
    "depends": [
        "purchase_discount",
    ],
    "author": "Alejandro Santana <alejandrosantana@anubia.es>",
    "category": "Purchase",
    "description": """
Shows purchase discounts in lines tree view within purchase form view.  
""",
    "init_xml": [],
    'update_xml': [
        'purchase_discount_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    #'certificate': 'certificate',
}
