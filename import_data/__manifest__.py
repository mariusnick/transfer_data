# Copyright 2022 OEC Romania SRL
# License OPL-1.0 or later
# (https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html#).

{
    "name": "Import Data",
    "version": "14.0.1.0.0",
    "category": "Operations",
    "author": "OEC Romania SRL",
    "website": "https://nexterp.ro",
    "support": "odoo_apps@nexterp.ro",
    "summary": """Import data from csv file in to models""",
    "depends": [],
    "data": [
        "security/ir.model.access.csv",
        "views/import_data_view.xml",
         "data/dict_template.xml",
    ],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["Nicolescu"],
    "images": ["import_icon.png"],
    "license": "OPL-1",
}
