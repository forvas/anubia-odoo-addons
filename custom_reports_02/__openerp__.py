# -*- coding: utf-8 -*-
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
    'name': 'Custom reports 02',
    'version': '0.1',
    'category': 'Customization',
    'description': '''
        This module customizes invoice report for an specific customer
        ==============================================================
        
            - Invoice report: allows to remove tax details in customer invoices (by specific customer request).
        
        **DISCLAIMER:**
        
        This module might result in illegal document in many cases, by hiding tax details.
        This is done as a request for a specific customer with unique legal circumstances and under their sole responsability.
        Therefore, use this module wisely and under your responsability. 
        ''',
    # 'complexity': 'normal',
    'license': 'AGPL-3',
    'author': 'Alejandro Santana <alejandrosantana@anubia.es>',
    'maintainer': 'Anubía, soluciones en la nube, SL',
    'website': 'http://www.anubia.es',
    'contributors': [
        'Alejandro Santana <alejandrosantana@anubia.es>',
    ],
    'depends': [
        'account',
        'base_setup',
        'report',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'account_report.xml',
        'views/report_invoice.xml',
        'views/account_invoice_view.xml',
     ],
    'demo': [],
    'test': [],
    'qweb' : [],
    'images': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
#    'certificate': 'certificate',
}
