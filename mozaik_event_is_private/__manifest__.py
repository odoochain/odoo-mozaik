# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Is Private",
    "summary": """
        This module adds the field is_private to Event.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # Odoo
        "event",
    ],
    "data": [
        "views/event_event.xml",
    ],
}
