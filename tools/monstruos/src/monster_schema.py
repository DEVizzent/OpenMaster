"""
Data models for monster stat blocks.

All data is stored as plain dicts for simplicity (JSON-serializable).
These constants and helpers define the expected structure.
"""

MONSTER_FIELDS = {
    "name": "",
    "name_en": "",
    "type": "",
    "subtype": None,
    "size": "",
    "alignment": "",
    "initiative": None,
    "initiative_bonus": None,
    "ac": 0,
    "hp": 0,
    "hp_formula": "",
    "speed": {"walk": None, "fly": None, "swim": None, "climb": None, "burrow": None},
    "attributes": {
        "STR": {"value": 10, "mod": 0, "save": 0},
        "DEX": {"value": 10, "mod": 0, "save": 0},
        "CON": {"value": 10, "mod": 0, "save": 0},
        "INT": {"value": 10, "mod": 0, "save": 0},
        "WIS": {"value": 10, "mod": 0, "save": 0},
        "CHA": {"value": 10, "mod": 0, "save": 0},
    },
    "skills": {},
    "vulnerabilities": [],
    "resistances": [],
    "immunities": [],
    "senses": {"darkvision": None, "blindsight": None, "truesight": None, "tremorsense": None, "pasiva": 10},
    "languages": "",
    "cr": "",
    "cr_numeric": 0.0,
    "xp": 0,
    "bc": 0,
    "equipment": [],
    "traits": [],
    "actions": [],
    "bonus_actions": [],
    "reactions": [],
    "legendary_actions": [],
    "legendary_resistances": 0,
    "habitat": [],
    "source": "",
    "description": "",
}

STAT_ABBR = {
    "Fue": "STR",
    "Des": "DEX",
    "Con": "CON",
    "Int": "INT",
    "Sab": "WIS",
    "Car": "CHA",
}

SIZE_ORDER = [
    "Diminuto",
    "Peque\u00f1o",
    "Mediano",
    "Mediano o Peque\u00f1o",
    "Grande",
    "Enorme",
    "Gargantuesco",
]

CR_FRACTIONS = {
    "0": 0.0,
    "1/8": 0.125,
    "1/4": 0.25,
    "1/2": 0.5,
    "ninguno": 0.0,
}

def cr_to_numeric(cr_str: str) -> float:
    """Convert CR string to float for comparison."""
    if not cr_str:
        return 0.0
    cr_str = cr_str.strip().lower()
    if cr_str in CR_FRACTIONS:
        return CR_FRACTIONS[cr_str]
    if "/" in cr_str:
        parts = cr_str.split("/")
        try:
            return float(parts[0]) / float(parts[1])
        except (ValueError, ZeroDivisionError):
            return 0.0
    try:
        return float(cr_str)
    except ValueError:
        return 0.0


def new_monster() -> dict:
    """Create a new monster dict with default values."""
    import copy
    return copy.deepcopy(MONSTER_FIELDS)


def normalize_name(name: str) -> str:
    """Normalize monster name for searching (remove accents, lowercase)."""
    import unicodedata
    import re
    if not name:
        return ""
    name = name.strip().lower()
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip, normalize whitespace)."""
    import re
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text
