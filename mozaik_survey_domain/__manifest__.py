# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Survey Domain",
    "summary": """
        Adds a domain on a survey to limit the access""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "mozaik_security_ama",
        "survey",
    ],
    "data": [
        "views/survey_survey.xml",
    ],
    "demo": [],
}
