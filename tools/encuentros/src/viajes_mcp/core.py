import random

RHYTHM_PROBABILITY = {
    "fast": 40,
    "normal": 60,
    "lively": 80,
}

DANGER_LEVEL_ORDER = ["low", "medium", "high", "lethal"]

ENCOUNTER_TYPES = ["social", "environment", "combat", "discovery"]

ENCOUNTER_WEIGHTS = {
    "low": {"social": 70, "environment": 15, "combat": 2.5, "discovery": 10},
    "medium": {"social": 40, "environment": 20, "combat": 20, "discovery": 15},
    "high": {"social": 15, "environment": 25, "combat": 45, "discovery": 15},
    "lethal": {"social": 5, "environment": 15, "combat": 70, "discovery": 10},
}

BOOST_SHIFT = {
    "positive": -1,
    "neutral": 0,
    "negative": 1,
}


def should_encounter(rhythm: str) -> bool:
    prob = RHYTHM_PROBABILITY.get(rhythm)
    if prob is None:
        raise ValueError(f"Invalid rhythm: {rhythm}. Must be one of {list(RHYTHM_PROBABILITY)}")
    return random.randint(1, 100) <= prob


def _shift_danger_level(danger_level: str, boost: str) -> str:
    level_idx = DANGER_LEVEL_ORDER.index(danger_level)
    shift = BOOST_SHIFT[boost]
    shifted_idx = max(0, min(len(DANGER_LEVEL_ORDER) - 1, level_idx + shift))
    return DANGER_LEVEL_ORDER[shifted_idx]


def roll_encounter_type(danger_level: str, boost: str = "neutral") -> str:
    if danger_level not in ENCOUNTER_WEIGHTS:
        raise ValueError(f"Invalid danger_level: {danger_level}. Must be one of {list(ENCOUNTER_WEIGHTS)}")
    if boost not in BOOST_SHIFT:
        raise ValueError(f"Invalid boost: {boost}. Must be one of {list(BOOST_SHIFT)}")

    adjusted_level = _shift_danger_level(danger_level, boost)
    weights = ENCOUNTER_WEIGHTS[adjusted_level]
    weights_list = [weights[t] for t in ENCOUNTER_TYPES]
    return random.choices(ENCOUNTER_TYPES, weights=weights_list, k=1)[0]
