# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Event Thesaurus Question",
    "summary": """
        This feature adds interests on every question
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        "website_event_questions",
        "mozaik_thesaurus",
    ],
    "data": [
        "views/event_event.xml",
        "views/event_question.xml",
        "views/event_type.xml",
    ],
}
