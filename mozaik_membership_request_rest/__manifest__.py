# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Membership Request Rest",
    "summary": """
        This module adds a controller for membership request REST services""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "base_rest",
        "base_rest_pydantic",
        "mozaik_membership_request",
        "mozaik_partner_global_opt_out",
    ],
    "data": [],
    "external_dependencies": {
        "python": [
            "pydantic",
        ]
    },
}
