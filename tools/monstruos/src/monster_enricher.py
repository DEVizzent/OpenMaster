"""
Enrich monster data by scraping English pages from aidedd.org.

For monsters with summarized/incomplete data, fetches the English
version of the page, parses full descriptions, and translates them
to Spanish following D&D 5.5 conventions.
"""
import re
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from bs4 import BeautifulSoup
from src.monster_schema import new_monster

# ═══════════════════════════════════════════════════════════
# D&D 5.5 Translation Glossary (EN → ES)
# ═══════════════════════════════════════════════════════════

DAMAGE_TYPES = {
    "Bludgeoning": "contundente",
    "Piercing": "perforante",
    "Slashing": "cortante",
    "Fire": "fuego",
    "Cold": "frío",
    "Lightning": "relámpago",
    "Thunder": "trueno",
    "Acid": "ácido",
    "Poison": "veneno",
    "Necrotic": "necrótico",
    "Radiant": "radiante",
    "Psychic": "psíquico",
    "Force": "fuerza",
}

CONDITIONS = {
    "Charmed": "Hechizado",
    "Frightened": "Asustado",
    "Paralyzed": "Paralizado",
    "Petrified": "Petrificado",
    "Poisoned": "Envenenado",
    "Prone": "Derribado",
    "Restrained": "Apresado",
    "Stunned": "Aturdido",
    "Unconscious": "Inconsciente",
    "Incapacitated": "Incapacitado",
    "Blinded": "Cegado",
    "Deafened": "Ensordecido",
    "Grappled": "Agarrado",
    "Invisible": "invisible",
    "Exhaustion": "Cansancio",
}

SIZES_EN = {
    "Tiny": "Diminuto",
    "Small": "Pequeño",
    "Medium": "Mediano",
    "Large": "Grande",
    "Huge": "Enorme",
    "Gargantuan": "Gargantuesco",
}

ALIGNMENTS_EN = {
    "Lawful Good": "legal bueno",
    "Lawful Neutral": "legal neutral",
    "Lawful Evil": "legal malvado",
    "Neutral Good": "neutral bueno",
    "Neutral": "neutral",
    "True Neutral": "neutral",
    "Neutral Evil": "neutral malvado",
    "Chaotic Good": "caótico bueno",
    "Chaotic Neutral": "caótico neutral",
    "Chaotic Evil": "caótico malvado",
    "Unaligned": "sin alineamiento",
    "Any Alignment": "cualquier alineamiento",
}

ABILITIES_EN = {
    "Str": "FUE", "Dex": "DES", "Con": "CON",
    "Int": "INT", "Wis": "SAB", "Cha": "CAR",
}

SKILLS_EN = {
    "Acrobatics": "Acrobacias", "Animal Handling": "Trato con animales",
    "Arcana": "Conocimiento arcano", "Athletics": "Atletismo",
    "Deception": "Engaño", "History": "Historia",
    "Insight": "Perspicacia", "Intimidation": "Intimidación",
    "Investigation": "Investigación", "Medicine": "Medicina",
    "Nature": "Naturaleza", "Perception": "Percepción",
    "Performance": "Interpretación", "Persuasion": "Persuasión",
    "Religion": "Religión", "Sleight of Hand": "Juego de manos",
    "Stealth": "Sigilo", "Survival": "Supervivencia",
}

SENSES_EN = {
    "Darkvision": "visión en la oscuridad",
    "Blindsight": "visión ciega",
    "Truesight": "visión verdadera",
    "Tremorsense": "sentir vibraciones",
    "Passive Perception": "Percepción pasiva",
}

SECTION_HEADERS = {
    "Traits": "Atributos",
    "Actions": "Acciones",
    "Bonus actions": "Acciones Bonus",
    "Bonus Actions": "Acciones Bonus",
    "Reactions": "Reacciones",
    "Legendary actions": "Acciones Legendarias",
    "Legendary Actions": "Acciones Legendarias",
    "Legendary action uses": "Usos de acciones legendarias",
}


def slugify(name: str) -> str:
    """Convert monster name to URL slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def fetch_page(url: str, timeout: int = 15) -> str | None:
    """Fetch a web page and return its HTML content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MonstruosMCP/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def feet_to_meters(text: str) -> str:
    """Convert feet to meters in D&D 5.5 Spanish convention (×0.3)."""
    def replace_ft(match):
        feet = int(match.group(1))
        meters = feet * 0.3
        if meters == int(meters):
            return f"{int(meters)} m"
        return f"{meters:.2f} m".replace(".00", "").replace(".50", ",50")
    return re.sub(r"(\d+)\s*ft\.?", replace_ft, text)


def translate_dnd_text(text: str) -> str:
    """Translate D&D 5.5 mechanical text from English to Spanish."""
    if not text:
        return ""

    t = text

    # Convert feet to meters
    t = feet_to_meters(t)

    # Replace section header keywords inline
    t = re.sub(r"\bHit(?! Points)\b", "Acierto", t)
    t = re.sub(r"\bMiss\b", "Fallo", t)

    # Attack roll patterns
    t = re.sub(r"Melee Attack Roll:", "Tirada de ataque cuerpo a cuerpo:", t)
    t = re.sub(r"Ranged Attack Roll:", "Tirada de ataque a distancia:", t)
    t = re.sub(r"Melee or Ranged Attack Roll:", "Tirada de ataque cuerpo a cuerpo o a distancia:", t)
    t = re.sub(r"Spell Attack Roll:", "Tirada de ataque de conjuro:", t)

    # Save patterns
    t = re.sub(r"(\w+) Saving Throw:", r"Tirada de salvación de \1:", t)
    t = re.sub(r"DC (\d+)", r"CD \1", t)
    t = re.sub(r"escape DC (\d+)", r"CD \1 para escapar", t)
    t = re.sub(r"spell save DC (\d+)", r"CD de salvación de conjuros \1", t)

    # Reach/range
    t = re.sub(r"\breach\b", "alcance", t)
    t = re.sub(r"\brange\b", "alcance a distancia", t)

    # Damage types
    for en, es in DAMAGE_TYPES.items():
        t = re.sub(rf"\b{en}\b(?=\s*(?:damage|$))", f"de daño de {es}", t)
    # Also handle "X damage" pattern directly
    for en, es in DAMAGE_TYPES.items():
        t = re.sub(rf"(\d+)\s*\([^)]+\)\s*{en}\s+damage", rf"\1 de daño de {es}", t)

    # Conditions
    for en, es in CONDITIONS.items():
        t = re.sub(rf"\b{en}\b(?=\s+condition)", f"{es}", t)
        t = re.sub(rf"the\s+{en}\s+condition", f"el estado de {es}", t)
        t = re.sub(rf"has the {en} condition", f"tiene el estado de {es}", t)
        t = re.sub(rf"have the {en} condition", f"tengan el estado de {es}", t)
        t = re.sub(rf"gains the {en} condition", f"obtiene el estado de {es}", t)

    # Sizes (in context of creature sizes)
    for en, es in SIZES_EN.items():
        t = re.sub(rf"\b{en}\b(?=\s+(?:or|and)\s+smaller|$)", es, t)

    # Abilities
    for en, es in ABILITIES_EN.items():
        t = re.sub(rf"\b{en}\b(?=\s+Saving Throw)", es, t)

    # Common mechanical terms
    t = t.replace("Hit Points", "puntos de golpe")
    t = t.replace("Hit Point", "punto de golpe")
    t = t.replace("hit points", "puntos de golpe")
    t = t.replace("saving throw", "tirada de salvación")
    t = t.replace("Saving Throw", "Tirada de salvación")
    t = t.replace("Damage", "daño")
    t = t.replace("damage", "daño")
    t = t.replace("Attack", "Ataque")
    t = t.replace("attack", "ataque")
    t = t.replace("target", "objetivo")
    t = t.replace("Target", "Objetivo")
    t = t.replace("Targets", "Objetivos")
    t = t.replace("creature", "criatura")
    t = t.replace("Creature", "Criatura")
    t = t.replace("creatures", "criaturas")
    t = t.replace("Creatures", "Criaturas")
    t = t.replace("within", "a")
    t = t.replace("feet of", "m o menos de")
    t = t.replace("foot of", "m o menos de")
    t = t.replace("feet", "m")
    t = t.replace("foot", "m")
    t = t.replace("emanating", "que se origina")
    t = t.replace("originating", "que se origina")
    t = t.replace("Emanation", "emanación")
    t = t.replace("Advantage", "ventaja")
    t = t.replace("Disadvantage", "desventaja")
    t = t.replace("advantage", "ventaja")
    t = t.replace("disadvantage", "desventaja")
    t = t.replace("on a successful save", "si tiene éxito")
    t = t.replace("on a failure", "si falla")
    t = t.replace("on a success", "si tiene éxito")
    t = t.replace("Failure:", "Fallo:")
    t = t.replace("Success:", "Éxito:")
    t = t.replace("Half damage", "Mitad del daño")
    t = t.replace("half damage", "mitad del daño")
    t = t.replace("Critical Hit", "golpe crítico")
    t = t.replace("takes", "recibe")
    t = t.replace("Action", "Acción")
    t = t.replace("action", "acción")
    t = t.replace("Bonus Action", "Acción Bonus")
    t = t.replace("bonus action", "acción bonus")
    t = t.replace("Reaction", "Reacción")
    t = t.replace("reaction", "reacción")
    t = t.replace("Immunities", "Inmunidades")
    t = t.replace("Resistances", "Resistencias")
    t = t.replace("Vulnerabilities", "Vulnerabilidades")
    t = t.replace("Skills", "Habilidades")
    t = t.replace("Senses", "Sentidos")
    t = t.replace("Languages", "Idiomas")
    t = t.replace("Speed", "Velocidad")
    t = t.replace("Armor Class", "CA")
    t = t.replace("Initiative", "Iniciativa")
    t = t.replace("day", "día")
    t = t.replace("Day", "Día")
    t = t.replace("At will:", "A voluntad:")
    t = t.replace("at will", "a voluntad")
    t = t.replace("Multiattack", "Ataque múltiple")
    t = t.replace("Spellcasting", "Lanzamiento de conjuros")
    t = t.replace("spellcasting ability", "aptitud mágica")
    t = t.replace("spellcasting", "lanzamiento de conjuros")
    t = t.replace("spell", "conjuro")
    t = t.replace("Spell", "Conjuro")
    t = t.replace("spells", "conjuros")
    t = t.replace("recharges", "recarga")
    t = t.replace("Recharges", "Recarga")
    t = t.replace("Recharge", "Recarga")
    t = t.replace("recharge", "recarga")
    t = t.replace("Legendary Resistance", "Resistencia legendaria")
    t = t.replace("Legendary Action Uses", "Usos de acciones legendarias")
    t = t.replace("undead", "muerto viviente")
    t = t.replace("Undead", "Muerto viviente")
    t = t.replace("concentration", "concentración")
    t = t.replace("Concentration", "Concentración")
    t = t.replace("Invisible", "invisible")
    t = t.replace("restrained", "apresado")
    t = t.replace("grappled", "agarrado")
    t = t.replace("frightened", "asustado")
    t = t.replace("charmed", "hechizado")
    t = t.replace("stunned", "aturdido")
    t = t.replace("poisoned", "envenenado")
    t = t.replace("prone", "derribado")
    t = t.replace("paralyzed", "paralizado")
    t = t.replace("petrified", "petrificado")

    # Clean up double spaces and fix spacing after periods
    t = re.sub(r"\s+", " ", t)
    t = t.replace(" .", ".")
    t = t.replace(" ,", ",")
    t = t.replace(" :", ":")
    t = t.strip()

    return t


def parse_english_page(html: str) -> dict | None:
    """Parse an English monster page from aidedd.org using HTML structure."""
    soup = BeautifulSoup(html, "html.parser")

    result = {
        "traits": [], "actions": [], "bonus_actions": [],
        "reactions": [], "legendary_actions": [], "legendary_action_uses": "",
        "flavor_text": "", "name_en": "", "habitat": [], "source": "", "treasure": "",
    }

    # Extract name from h1 or title
    h1 = soup.find("h1")
    if h1:
        result["name_en"] = h1.get_text(strip=True)

    # Find the main content: same structure as Spanish page
    sans = soup.find("div", class_="sansSerif")
    if not sans:
        return result

    # Parse sections from h2.rub elements (same logic as Spanish parser)
    h2s = sans.find_all("h2", class_="rub")
    if not h2s:
        # Try finding any h2
        h2s = sans.find_all("h2")

    for h2 in h2s:
        section_name = h2.get_text(strip=True).lower()
        entries = _get_section_entries(h2)

        if "trait" in section_name:
            result["traits"] = entries
        elif "legendary action" in section_name or "legendary action uses" in section_name:
            if "uses" in section_name:
                result["legendary_action_uses"] = " ".join(entries)
            else:
                result["legendary_actions"] = entries
        elif "bonus" in section_name:
            result["bonus_actions"] = entries
        elif "reaction" in section_name:
            result["reactions"] = entries
        elif "action" in section_name:
            result["actions"] = entries

    # Extract habitat/source/treasure from dedicated divs or full text
    # English pages have div.habitat, div.source, div.treasure
    habitat_div = soup.find("div", class_="habitat")
    if habitat_div:
        hab_text = habitat_div.get_text(strip=True)
        hab_text = hab_text.replace("Habitat:", "").replace("Habitat", "").strip().rstrip(".")
        result["habitat"] = [h.strip() for h in hab_text.split(",") if h.strip()]

    source_div = soup.find("div", class_="source")
    if source_div:
        result["source"] = source_div.get_text(strip=True)

    # Fallback: search full text
    full_text = sans.get_text() if sans else soup.get_text()

    if not result["habitat"]:
        hab_match = re.search(r"Habitat:\s*(.+?)\s*(?:Monster Manual|Player|Treasure|Source|\[[A-Z]{2}\]|\n|$)", full_text)
        if hab_match:
            hab_text = hab_match.group(1).strip().rstrip(".")
            result["habitat"] = [h.strip() for h in hab_text.split(",") if h.strip()]

    if not result["source"]:
        src_match = re.search(r"(Monster Manual \d{4}[^\n\]\[]*)", full_text)
        if src_match:
            result["source"] = src_match.group(1).strip()
        else:
            src_match = re.search(r"(Player.*?Handbook \d{4}[^\n\]\[]*)", full_text)
            if src_match:
                result["source"] = src_match.group(1).strip()

    if not result.get("treasure"):
        treas_match = re.search(r"Treasure:\s*(.+?)\s*(?:Monster Manual|Player|Source|\[[A-Z]{2}\]|\n|$)", full_text)
        if treas_match:
            result["treasure"] = treas_match.group(1).strip()

    return result


def _get_section_entries(h2) -> list[str]:
    """Get English text entries from an h2.rub section element."""
    entries = []
    sibling = h2.next_sibling
    while sibling:
        if hasattr(sibling, "name"):
            if sibling.name == "h2" and "rub" in sibling.get("class", []):
                break
            if sibling.name == "p":
                text = sibling.get_text(strip=True)
                if text:
                    entries.append(text)
            elif sibling.name == "div" and "legend" in sibling.get("class", []):
                leg_text = sibling.get_text(strip=True)
                if leg_text:
                    entries.append(leg_text)
        elif isinstance(sibling, str):
            text = str(sibling).strip()
            if text:
                entries.append(text)
        sibling = sibling.next_sibling

    # If no <p> tags found, try <br> separated content
    if not entries:
        raw = []
        sib = h2.next_sibling
        while sib:
            if hasattr(sib, "name") and sib.name == "h2" and "rub" in sib.get("class", []):
                break
            if hasattr(sib, "name"):
                raw.append(str(sib))
            elif isinstance(sib, str):
                raw.append(str(sib))
            sib = sib.next_sibling
        raw_text = "".join(raw)
        parts = re.split(r"<br\s*/?>", raw_text)
        for part in parts:
            text = re.sub(r"<[^>]+>", "", part).strip()
            text = text.replace("\u2013", "-").replace("\u2014", "-")
            if text and not text.startswith("Habitat:") and not text.startswith("Treasure:"):
                entries.append(text)

    return entries


def parse_entries_into_name_desc(lines: list[str]) -> list[dict]:
    """Parse raw English entry lines into name/description dicts."""
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Pattern: "Name. Description..." or "Name (X/Day). Description..."
        # Name can contain parentheses and commas but ends at ". " (period+space)
        # Be careful not to split on periods in numbers (e.g., "1.50")
        match = re.match(r"^(.+?)\.\s+(.+)$", line)
        if match:
            name = match.group(1).strip()
            desc = match.group(2).strip()
            # Don't split if name is too short (might be number)
            if len(name) > 2:
                entries.append({"name": name, "description": desc})
                continue

        # If line starts with a known pattern like "Melee Attack Roll:..." it's a continuation
        if re.match(r"^(Melee|Ranged|Hit|Miss|DC|Range|Reach)", line):
            if entries:
                entries[-1]["description"] += " " + line
            continue

        # Standalone entry without clear split
        name = re.sub(r"\.$", "", line).strip()
        entries.append({"name": name, "description": ""})

    # Merge continuation lines that got split (lines without a name)
    merged = []
    for entry in entries:
        if entry["name"] and not entry["description"]:
            if merged and re.match(r"^[A-Za-z]", entry["name"]):
                merged[-1]["description"] += " " + entry["name"]
                continue
        merged.append(entry)

    return merged


def normalize_name_for_match(name: str) -> str:
    """Normalize a name for fuzzy matching."""
    import unicodedata
    n = name.lower().strip()
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode("ascii")
    n = re.sub(r"[^a-z0-9\s]", "", n)
    n = re.sub(r"\s+", " ", n)
    return n.strip()


def match_entries(es_entries: list[dict], en_entries: list[dict]) -> list[dict]:
    """Match and merge Spanish entries with translated English entries.

    Returns enriched Spanish entries with descriptions filled in.
    """
    result = []
    en_used = set()

    for es_entry in es_entries:
        es_name_norm = normalize_name_for_match(es_entry["name"])
        best_match = None
        best_score = 0

        for ei, en_entry in enumerate(en_entries):
            if ei in en_used:
                continue
            en_name_translated = translate_dnd_text(en_entry["name"])
            en_name_norm = normalize_name_for_match(en_name_translated)

            # Score: how many words overlap between normalized names
            es_words = set(es_name_norm.split())
            en_words = set(en_name_norm.split())
            if not es_words or not en_words:
                continue

            overlap = es_words & en_words
            score = len(overlap) / max(len(es_words), len(en_words))

            # Bonus for same word count
            if len(es_words) == len(en_words):
                score += 0.3

            if score > best_score and score > 0.3:
                best_score = score
                best_match = ei

        if best_match is not None:
            en_entry = en_entries[best_match]
            en_used.add(best_match)

            # If Spanish entry already has a non-empty description, keep it
            existing_desc = es_entry.get("description", "")
            new_desc = translate_dnd_text(en_entry["description"])

            # Only replace if the existing description is empty or very short
            if existing_desc and len(existing_desc) > len(new_desc) * 0.5:
                final_desc = existing_desc
            elif existing_desc and len(existing_desc) > 20:
                final_desc = existing_desc
            else:
                final_desc = new_desc

            result.append({
                "name": es_entry["name"],
                "description": final_desc,
            })
        else:
            result.append(es_entry)

    # Add unmatched English entries
    for ei, en_entry in enumerate(en_entries):
        if ei not in en_used:
            result.append({
                "name": translate_dnd_text(en_entry["name"]),
                "description": translate_dnd_text(en_entry["description"]),
            })

    return result


def needs_metadata_enrichment(monster: dict) -> bool:
    """Check if monster is missing name_en or habitat."""
    return not monster.get("name_en") or not monster.get("habitat")


def needs_content_enrichment(monster: dict) -> bool:
    """Check if monster has sections with all-empty descriptions."""
    sections = ["traits", "actions", "bonus_actions", "reactions", "legendary_actions"]
    for section in sections:
        entries = monster.get(section, [])
        if entries and all(not e.get("description") for e in entries):
            return True
    return False


def enrich_metadata(monster: dict, en_data: dict) -> dict:
    """Fill in name_en, habitat, source from English data."""
    if not monster.get("name_en") and en_data.get("name_en"):
        monster["name_en"] = en_data["name_en"]
    if not monster.get("habitat") and en_data.get("habitat"):
        monster["habitat"] = en_data["habitat"]
    if not monster.get("source") and en_data.get("source"):
        monster["source"] = en_data["source"]
    return monster


def enrich_content(monster: dict, en_data: dict) -> dict:
    """Fill empty descriptions from translated English data.

    For sections where ALL entries have empty descriptions, we try to match
    English entries to existing Spanish names. If matching fails, we add
    translated English entries alongside.
    """
    section_map = [
        ("traits", "traits"),
        ("actions", "actions"),
        ("bonus_actions", "bonus_actions"),
        ("reactions", "reactions"),
        ("legendary_actions", "legendary_actions"),
    ]

    for es_key, en_key in section_map:
        en_raw = en_data.get(en_key, [])
        if not en_raw:
            continue

        en_entries = parse_entries_into_name_desc(en_raw)
        if not en_entries:
            continue

        es_entries = monster.get(es_key, [])
        all_empty = es_entries and all(not e.get("description") for e in es_entries)

        if all_empty:
            # Try matching, fall back to adding translated entries
            monster[es_key] = match_entries(es_entries, en_entries)
        elif not es_entries and en_entries:
            # Empty section entirely, just add translated entries
            translated = []
            for e in en_entries:
                translated.append({
                    "name": translate_dnd_text(e["name"]),
                    "description": translate_dnd_text(e["description"]),
                })
            monster[es_key] = translated

    if en_data.get("flavor_text") and not monster.get("description"):
        monster["description"] = translate_dnd_text(en_data["flavor_text"])

    return monster


def enrich_monster(monster: dict, html: str) -> dict:
    """Enrich monster from English HTML page (both metadata and content)."""
    en_data = parse_english_page(html)
    if not en_data:
        return monster
    monster = enrich_metadata(monster, en_data)
    if needs_content_enrichment(monster):
        monster = enrich_content(monster, en_data)
    return monster


def slugify_es(name: str) -> str:
    """Convert Spanish monster name to URL slug for aidedd.org."""
    import unicodedata
    slug = name.lower().strip()
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def discover_en_url(es_name: str) -> str | None:
    """Fetch Spanish page and extract the English page URL."""
    es_slug = slugify_es(es_name)
    url = f"https://www.aidedd.org/monster/es/{es_slug}"
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    for div in soup.find_all("div", class_="trad"):
        a = div.find("a")
        if a:
            text = a.get_text(strip=True)
            if "EN" in text or "[EN]" in text:
                href = a.get("href", "")
                if href.startswith("./"):
                    return f"https://www.aidedd.org/monster{href[1:]}"
                elif href.startswith("/"):
                    return f"https://www.aidedd.org{href}"
                elif not href.startswith("http"):
                    return f"https://www.aidedd.org/monster/{href}"
    return None


def enrich_content_force(monster: dict, en_data: dict) -> dict:
    """Force-fill all sections from translated English data, replacing existing if empty."""
    section_map = [
        ("traits", "traits"),
        ("actions", "actions"),
        ("bonus_actions", "bonus_actions"),
        ("reactions", "reactions"),
        ("legendary_actions", "legendary_actions"),
    ]

    for es_key, en_key in section_map:
        en_raw = en_data.get(en_key, [])
        if not en_raw:
            continue

        en_entries = parse_entries_into_name_desc(en_raw)
        if not en_entries:
            continue

        es_entries = monster.get(es_key, [])
        all_empty = es_entries and all(not e.get("description") for e in es_entries)

        if all_empty or not es_entries:
            translated = []
            for e in en_entries:
                translated.append({
                    "name": translate_dnd_text(e["name"]),
                    "description": translate_dnd_text(e["description"]),
                })
            monster[es_key] = translated

    if en_data.get("flavor_text") and not monster.get("description"):
        monster["description"] = translate_dnd_text(en_data["flavor_text"])

    return monster


def process_all(monsters: list[dict], delay: float = 1.0) -> tuple[list[dict], dict]:
    """Process all monsters, enriching from English pages.

    Returns (enriched_monsters, stats).
    """
    stats = {
        "total": len(monsters),
        "metadata_enriched": 0,
        "content_enriched": 0,
        "skipped": 0,
        "failed": 0,
        "no_en_name": 0,
    }
    enriched = []
    total = len(monsters)

    for i, m in enumerate(monsters):
        needs_meta = needs_metadata_enrichment(m)
        needs_content = needs_content_enrichment(m)

        if not needs_meta and not needs_content:
            enriched.append(m)
            stats["skipped"] += 1
            continue

        en_name = m.get("name_en", "")
        url = None

        if en_name:
            slug = slugify(en_name)
            url = f"https://www.aidedd.org/monster/{slug}"
        else:
            # Try to discover EN URL from Spanish page
            url = discover_en_url(m["name"])
            if url:
                en_name = url.rstrip("/").split("/")[-1].replace("-", " ").title()
                needs_meta = True
                needs_content = True  # Force content enrichment when discovered

        if not url:
            stats["no_en_name"] += 1
            enriched.append(m)
            continue

        print(f"[{i+1}/{total}] {m['name']} -> {en_name} ... ", end="", flush=True)

        html = fetch_page(url)
        if html:
            en_data = parse_english_page(html)
            if en_data:
                m = enrich_metadata(m, en_data)
                stats["metadata_enriched"] += 1
                if needs_content:
                    m = enrich_content_force(m, en_data)
                    stats["content_enriched"] += 1
                print("OK")
            else:
                stats["failed"] += 1
                print("PARSE_FAIL")
        else:
            stats["failed"] += 1
            print("FETCH_FAIL")

        enriched.append(m)
        time.sleep(delay)

    return enriched, stats
