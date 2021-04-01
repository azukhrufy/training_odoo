# -*- coding: utf-8 -*-
{
    'name': "Kursus Odoo",

    'summary': """
        Modul untuk Kursus Odoo""",

    'description':"""
        Modul ini berfungsi untuk menjalankan technical documentation pada website resmi odoo.com. Bahan yang dipelajari adalah :
        - ORM
        - Berbagai View
        - Report
        - Wizard
        - Dll
    """,
    'author': "Ananda Zukhruf Awalwi",
    'website': "http://zukhrufblogindonesia.blogspot.com/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mail'],
    'data': [
        #'security/security.xml',
        #'security/ir.model.access.csv',
        'report/action_report.xml',
        'report/report_sesi.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/sesi.xml',
        'views/partner.xml',
        'wizard/wizard_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application" : True,
}