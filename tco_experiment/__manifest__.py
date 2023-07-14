# -*- coding: utf-8 -*-
{
    'name': "Experiment - TUICO",
    'summary': """Experiment model""",
    'description': """Managing Experiment information""",
    'author': "tuicovn.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product', 'stock', 'portal', 'mail', 'utm',
    ],
    'data': [
        'views/tco_compound_method.xml',
        'security/tco_experiment_security.xml',
        'security/ir.model.access.csv',
        'views/tco_compound.xml',
        'views/tco_project.xml',
        'views/tco_mooney.xml',
        'views/tco_experiment_views.xml',
        'views/tco_task.xml',
        'views/tco_testing.xml',
        'views/tco_result.xml',
        'views/tco_method_title.xml',
        'report/tco_experiment_report.xml',
        'report/report_task.xml',
        'report/report.xml',
        'data/data.xml',
        'views/tco_view.xml',

    ],

    # 'qweb': ['static/src/xml/*.xml'],
    'assets': {
        'web.assets_backend': [

        ],
        "tco_experiment.tco_report_layout": [
            "/tco_experiment/static/src/scss/report_qweb_pdf.scss",
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
