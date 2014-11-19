# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Alejandro Santana <alejandrosantana@anubia.es>
#    Copyright (c) All rights reserved:
#        (c) 2014      Anubía, soluciones en la nube,SL (http://www.anubia.es)
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
    # invoice_analysis_group_by_location
    "name": "Allow group by invoice address details in invoice analysis",
    "version": "1.3",
    "depends": [
        "account",
        "sale",
    ],
    "author": "Alejandro Santana <alejandrosantana@anubia.es>",
    "category": "Product/Sale/Accounting",
    "description": """
This module aims to allow grouping by country in invoice analysis report.
This country is made available in invoice form, and it's taken from the
invoice address (where the 'country_id' field is now mandatory).
""",
    "init_xml": [],
    'update_xml': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'report/account_invoice_report_country_view.xml',
        'account_invoice_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    #'certificate': 'certificate',
}
