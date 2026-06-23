"""
data_loader.py
==============
Loads reference data from the data/ folder.
Used by db_service.py to resolve personality labels.
"""

import json


def load_personality_labels() -> dict:
    """Returns dict of personality type codes to labels. e.g. {"ANL": "Analytical"}"""
    with open("data/personality.json") as f:
        data = json.load(f)
    return data.get("personality_types", {})