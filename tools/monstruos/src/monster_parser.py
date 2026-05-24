"""
Parse the aidedd.org monster list HTML into structured monster dicts.
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup
from src.monster_schema import (
    new_monster, STAT_ABBR, cr_to_numeric, SIZE_ORDER,
)


class MonsterParser:
    """Parses the aidedd.org monster list HTML file."""

    def parse_file(self, filepath: str, enrichment_path: str | None = None) -> list[dict]:
        """Parse an HTML file and return list of monster dicts."""
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        monsters = self.parse_html(html)
        if enrichment_path:
            self._enrich(monsters, enrichment_path)
        return monsters

    def parse_html(self, html: str) -> list[dict]:
        """Parse HTML string and return list of monster dicts."""
        soup = BeautifulSoup(html, "html.parser")
        monsters = []

        for bloc in soup.find_all("div", class_="bloc"):
            try:
                monster = self._parse_bloc(bloc)
                if monster and monster["name"]:
                    monsters.append(monster)
            except Exception:
                continue

        return monsters

    @staticmethod
    def _enrich(monsters: list[dict], enrichment_path: str):
        """Merge English names and habitats from enrichment JSON."""
        import json
        with open(enrichment_path, "r", encoding="utf-8") as f:
            enrichment = json.load(f)
        for m in monsters:
            if m["name"] in enrichment:
                m["name_en"] = enrichment[m["name"]].get("name_en", "")
                m["habitat"] = enrichment[m["name"]].get("habitat", [])

    def _parse_bloc(self, bloc) -> dict | None:
        """Parse a single div.bloc into a monster dict."""
        m = new_monster()

        jaune = bloc.find("div", class_="jaune")
        if not jaune:
            return None

        inner = jaune.find("div", class_=lambda c: c in ("", "double"))
        if not inner:
            inner = jaune.find("div")
        if not inner:
            return None

        # Name
        h1 = inner.find("h1")
        if not h1:
            return None
        m["name"] = h1.get_text(strip=True)

        sans = inner.find("div", class_="sansSerif")
        if not sans:
            return None

        # Parse the red section (stats)
        red = sans.find("div", class_="red")
        if red:
            self._parse_red_section(red, m)

        # Parse sections: Atributos, Acciones, Acciones Bonus, Reacciones, Acciones Legendarias
        self._parse_sections(sans, m)

        # English name from adjacent links (if present)
        en_link = h1.find_next("a")
        if en_link and "EN" in en_link.get_text(strip=True):
            pass

        return m

    def _parse_red_section(self, red, m: dict):
        """Parse the div.red containing stats."""
        # Type, size, alignment
        type_div = red.find("div", class_="type")
        if type_div:
            type_text = type_div.get_text(strip=True)
            self._parse_type_line(type_text, m)

        # Initiative
        init_div = red.find("div", class_="init")
        if init_div:
            init_text = init_div.get_text(strip=True)
            m["initiative"] = self._parse_initiative(init_text)

        # Now parse the <strong> and <br> based fields
        # CA, PG, Velocidad, Habilidades, Resistencias, Inmunidades,
        # Sentidos, Idiomas, VD, Equipamiento
        self._parse_strong_fields(red, m)

        # Stats table
        self._parse_stats_table(red, m)

    KNOWN_TYPES = [
        "Aberración", "Autómata", "Bestia", "Celestial", "Cieno", "Dragón",
        "Elemental", "Enjambre de Bestias Diminutas", "Enjambre de Bestias Pequeñas",
        "Enjambre de Infernales Medianos", "Enjambre de Infernales Pequeños",
        "Enjambre de Monstruosidades Diminutas", "Enjambre de Muertos vivientes Diminutos",
        "Enjambre", "Feérico", "Gigante", "Humanoide", "Infernal",
        "Monstruosidad", "Muerto viviente", "Planta",
    ]

    def _parse_type_line(self, text: str, m: dict):
        """Parse type line like 'Elemental Mediano, neutral' or 'Bestia (dinosaurio) Grande, sin alineamiento'."""
        rest = text

        # Extract subtype in parentheses
        subtype_match = re.match(r"(.+?)\s*\((.+?)\)\s+(.*)", text)
        if subtype_match:
            before_paren = subtype_match.group(1).strip()
            m["subtype"] = subtype_match.group(2).strip()
            rest = before_paren + " " + subtype_match.group(3).strip()
        else:
            rest = text

        # Try to match a known type (multi-word types first)
        m["type"] = ""
        for t in sorted(self.KNOWN_TYPES, key=len, reverse=True):
            if rest.startswith(t):
                m["type"] = t
                rest = rest[len(t):].strip()
                break

        if not m["type"]:
            # Fallback: first word is type
            parts = rest.split(None, 1)
            if parts:
                m["type"] = parts[0]
                rest = parts[1].strip() if len(parts) > 1 else ""

        # Parse size and alignment from rest
        size_found = None
        for size in sorted(SIZE_ORDER, key=len, reverse=True):
            if rest.startswith(size):
                size_found = size
                break

        if size_found:
            m["size"] = size_found
            rest = rest[len(size_found):].strip()
            # Handle alternative sizes like "Grande o Gargantuesco"
            if rest.startswith("o "):
                alt_match = re.match(r"o\s+(\w+)\s*(,?\s*)", rest)
                if alt_match:
                    alt_size = alt_match.group(1)
                    rest = rest[alt_match.end():].strip()
                    m["size"] = f"{size_found} o {alt_size}"
            if rest.startswith(","):
                rest = rest[1:].strip()
            m["alignment"] = rest.lower().strip()
        else:
            comma = rest.find(",")
            if comma != -1:
                m["size"] = rest[:comma].strip()
                m["alignment"] = rest[comma + 1:].strip().lower()
            else:
                m["size"] = rest
                m["alignment"] = ""

    def _parse_initiative(self, text: str) -> int | None:
        """Parse initiative like 'Iniciativa+3 (13)' or 'Iniciativa -2 (8)'."""
        text = self._normalize_dashes(text)
        match = re.search(r"Iniciativa\s*([+-]?\d+)\s*\((\d+)\)", text)
        if match:
            return int(match.group(1))
        match = re.search(r"Iniciativa\s*([+-]?\d+)", text)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _normalize_dashes(text: str) -> str:
        """Replace unicode dashes with ASCII minus."""
        return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")

    def _parse_strong_fields(self, red, m: dict):
        """Parse <strong> labeled fields: CA, PG, Velocidad, Habilidades, etc.

        Iterates through children of the red div, capturing <strong> labels
        and their following text (siblings after the <strong> element).
        """
        for child in red.children:
            if not hasattr(child, "name"):
                continue

            if child.name == "strong":
                label = child.get_text(strip=True)
                # Get text after this strong element (following siblings until next strong or br)
                value = self._get_text_after(child)

                if label == "CA":
                    m["ac"] = self._extract_first_number(value)
                elif label == "PG":
                    hp_match = re.search(r"(\d+)", value)
                    if hp_match:
                        m["hp"] = int(hp_match.group(1))
                    formula_match = re.search(r"\((.+?)\)", value)
                    if formula_match:
                        m["hp_formula"] = formula_match.group(1)
                elif label == "Velocidad":
                    self._parse_speed(value, m)
                elif label == "Habilidades":
                    m["skills"] = self._parse_skills(value)
                elif label == "Vulnerabilidades":
                    m["vulnerabilities"] = self._split_csv(value)
                elif label == "Resistencias":
                    m["resistances"] = self._split_csv(value)
                elif label == "Inmunidades":
                    m["immunities"] = self._split_csv(value)
                elif label == "Sentidos":
                    m["senses"] = self._parse_senses(value)
                elif label == "Idiomas":
                    lang = value.strip()
                    if lang in ("\u2014", "-", "\u2014"):
                        lang = ""
                    m["languages"] = lang
                elif label == "VD":
                    self._parse_cr(value, m)
                elif label == "Equipamiento":
                    m["equipment"] = self._split_csv(value)

        # Clean up languages value
        if m["languages"] in ("ninguno", "ninguno."):
            m["languages"] = "ninguno"

    def _get_text_after(self, element) -> str:
        """Get text content after an element, up to the next <strong> or <br>."""
        parts = []
        sibling = element.next_sibling
        while sibling:
            if hasattr(sibling, "name"):
                if sibling.name in ("strong", "br", "h2", "div"):
                    break
                parts.append(sibling.get_text())
            elif isinstance(sibling, str):
                parts.append(str(sibling))
            sibling = sibling.next_sibling
        return "".join(parts).strip()

    def _parse_speed(self, line: str, m: dict):
        """Parse speed line like '6 m, volar 15 m, nadar 12 m'."""
        line = line.replace("Velocidad ", "", 1).strip()
        parts = line.split(",")

        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Try: "6 m", "volar 15 m", "nadar 12 m", "trepar 9 m", "excavar 3 m"
            if "volar" in part or "volando" in part or ("fly" in part.lower()):
                speed_type = "fly"
            elif "nadar" in part or "nataci" in part or ("swim" in part.lower()):
                speed_type = "swim"
            elif "trepar" in part or "escalar" in part or ("climb" in part.lower()):
                speed_type = "climb"
            elif "excavar" in part or "cavar" in part or ("burrow" in part.lower()):
                speed_type = "burrow"
            else:
                speed_type = "walk"

            # Extract the number (first number in meters)
            num_match = re.search(r"(\d+[\.,]?\d*)", part)
            if num_match:
                val = float(num_match.group(1).replace(",", "."))
                if speed_type == "walk":
                    m["speed"]["walk"] = val
                else:
                    m["speed"][speed_type] = val

        # Also check for levitation
        if "levitar" in line.lower() and m["speed"]["fly"] is not None:
            pass

    def _parse_stats_table(self, red, m: dict):
        """Parse the stats table (car1-car6 divs with attribute values)."""
        attr_data = {
            "Fue": {"value": None, "mod": None, "save": None},
            "Des": {"value": None, "mod": None, "save": None},
            "Con": {"value": None, "mod": None, "save": None},
            "Int": {"value": None, "mod": None, "save": None},
            "Sab": {"value": None, "mod": None, "save": None},
            "Car": {"value": None, "mod": None, "save": None},
        }

        # Find all car divs in order
        car_divs = []
        for cls in ["car1", "car2", "car3", "car4", "car5", "car6"]:
            divs = red.find_all("div", class_=cls)
            car_divs.extend(divs)

        # Also find just "car" headers
        # We need to reconstruct the table from the HTML structure
        # The table has a header row and then data rows
        # Each attribute row: car1(name) car2(value) car3(mod) car3(save)
        # Or: car4(name) car5(value) car6(mod) car6(save)

        # Better approach: find all div children and parse by class order
        all_car_divs = red.find_all("div", class_=re.compile(r"^car\d?$"))

        # Simpler: parse by looking at the text within the div
        all_car_divs = []
        for div in red.find_all("div"):
            cls = div.get("class", [])
            if cls and re.match(r"^car\d?$", cls[0]):
                all_car_divs.append(div)

        i = 0
        while i < len(all_car_divs):
            div = all_car_divs[i]
            cls = div.get("class", [""])[0]
            text = div.get_text(strip=True)

            if cls == "car1":
                stat_name = text
                if i + 2 < len(all_car_divs):
                    val_text = all_car_divs[i + 1].get_text(strip=True)
                    mod_text = all_car_divs[i + 2].get_text(strip=True)
                    save_text = mod_text
                    if i + 3 < len(all_car_divs) and all_car_divs[i + 3].get("class", [""])[0] == "car3":
                        save_text = all_car_divs[i + 3].get_text(strip=True)
                        i += 1

                    if stat_name in attr_data:
                        attr_data[stat_name]["value"] = self._parse_int(val_text)
                        attr_data[stat_name]["mod"] = self._parse_int(mod_text)
                        attr_data[stat_name]["save"] = self._parse_int(save_text)
                    i += 3
                else:
                    i += 1
            elif cls == "car4":
                stat_name = text
                if i + 2 < len(all_car_divs):
                    val_text = all_car_divs[i + 1].get_text(strip=True)
                    mod_text = all_car_divs[i + 2].get_text(strip=True)
                    save_text = mod_text
                    if i + 3 < len(all_car_divs) and all_car_divs[i + 3].get("class", [""])[0] == "car6":
                        save_text = all_car_divs[i + 3].get_text(strip=True)
                        i += 1

                    if stat_name in attr_data:
                        attr_data[stat_name]["value"] = self._parse_int(val_text)
                        attr_data[stat_name]["mod"] = self._parse_int(mod_text)
                        attr_data[stat_name]["save"] = self._parse_int(save_text)
                    i += 3
                else:
                    i += 1
            else:
                i += 1

        # Convert to output format
        for abbr, data in attr_data.items():
            eng = STAT_ABBR.get(abbr, abbr)
            if data["value"] is not None:
                m["attributes"][eng] = {
                    "value": data["value"],
                    "mod": data["mod"] or 0,
                    "save": data["save"] or 0,
                }

    def _parse_skills(self, text: str) -> dict:
        """Parse skills like 'Percepción +5, Sigilo +10' or 'Conocimiento arcano +3, Naturaleza +5'."""
        skills = {}
        if not text:
            return skills

        # Split by comma, being careful with multi-word skill names
        parts = re.split(r",\s*(?=[A-ZÁÉÍÓÚ])", text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            match = re.search(r"(.+?)\s+([+-]?\d+)$", part)
            if match:
                name = match.group(1).strip()
                value = int(match.group(2))
                skills[name] = value
        return skills

    def _parse_senses(self, text: str) -> dict:
        """Parse senses like 'visión en la obscuridad 18 m, Percepción pasiva 12'."""
        senses = {"darkvision": None, "blindsight": None, "truesight": None, "tremorsense": None, "pasiva": 10}
        if not text:
            return senses

        # Parse passive perception
        pp_match = re.search(r"Percepci[oó]n\s+pasiva\s+(\d+)", text)
        if pp_match:
            senses["pasiva"] = int(pp_match.group(1))

        # Darkvision
        dv_match = re.search(r"visi[oó]n\s+en\s+la\s+obscuridad\s+(\d+)", text)
        if dv_match:
            senses["darkvision"] = int(dv_match.group(1))

        # Blindsight
        bs_match = re.search(r"visi[oó]n\s+ciega\s+(\d+)", text)
        if bs_match:
            senses["blindsight"] = int(bs_match.group(1))

        # Truesight
        ts_match = re.search(r"visi[oó]n\s+verdadera\s+(\d+)", text)
        if ts_match:
            senses["truesight"] = int(ts_match.group(1))

        # Tremorsense
        tr_match = re.search(r"sentir\s+vibraciones\s+(\d+)", text)
        if tr_match:
            senses["tremorsense"] = int(tr_match.group(1))

        return senses

    def _parse_cr(self, value: str, m: dict):
        """Parse challenge rating value like '1/4 (PX 50; BC +2)' or '10 (PX 5900; BC +4)'."""
        value = self._normalize_dashes(value)

        cr_match = re.search(r"^([\d/]+|ninguno)", value)
        if cr_match:
            cr_str = cr_match.group(1)
            m["cr"] = cr_str
            m["cr_numeric"] = cr_to_numeric(cr_str)

        xp_match = re.search(r"PX\s+([\d\s\u202f]+)", value)
        if xp_match:
            xp = xp_match.group(1).replace("\u202f", "").replace(" ", "").strip()
            try:
                m["xp"] = int(xp)
            except ValueError:
                pass

        bc_match = re.search(r"BC\s+\+(\d+)", value)
        if bc_match:
            m["bc"] = int(bc_match.group(1))

    def _parse_sections(self, sans, m: dict):
        """Parse Atributos, Acciones, Acciones Bonus, Reacciones, Acciones Legendarias sections."""
        # Find all h2.rub elements
        for h2 in sans.find_all("h2", class_="rub"):
            section_name = h2.get_text(strip=True).lower()
            content = self._get_section_content(h2)

            if "atributo" in section_name:
                m["traits"] = self._parse_entries(content)
            elif "legendaria" in section_name:
                m["legendary_actions"] = self._parse_entries(content)
                # Check for legendary uses count
                legend_div = h2.find_next("div", class_="legend")
                if legend_div:
                    uses_match = re.search(r"(\d+)", legend_div.get_text())
                    if uses_match:
                        m["legendary_resistances"] = int(uses_match.group(1))
            elif "bonus" in section_name:
                m["bonus_actions"] = self._parse_entries(content)
            elif "reacci" in section_name:
                m["reactions"] = self._parse_entries(content)
            elif "acci" in section_name:
                if not m["actions"]:
                    m["actions"] = self._parse_entries(content)
                else:
                    # Duplicate "Acciones" section (some entries have it twice)
                    m["bonus_actions"].extend(self._parse_entries(content))

        # Also look for legendary resistances in traits
        for trait in m["traits"]:
            if "legendaria" in trait["name"].lower():
                lr_match = re.search(r"(\d+)/d[ií]a", trait["name"])
                if lr_match:
                    m["legendary_resistances"] = int(lr_match.group(1))

    def _get_section_content(self, h2) -> list:
        """Get content between h2.rub and the next h2.rub or end of parent."""
        entries = []
        sibling = h2.next_sibling
        while sibling:
            if hasattr(sibling, "name") and sibling.name == "h2" and "rub" in sibling.get("class", []):
                break
            if hasattr(sibling, "name"):
                if sibling.name == "p":
                    text = sibling.get_text(" ", strip=True)
                    if text:
                        entries.append(self._parse_entry(text))
                elif sibling.name == "div" and "legend" in sibling.get("class", []):
                    pass  # Skip legend div, it's just metadata
            elif hasattr(sibling, "string") or isinstance(sibling, str):
                text = str(sibling).strip()
                if text:
                    entries.append(self._parse_entry(text))
            sibling = sibling.next_sibling

        # Also check for <br> separated line entries (not in <p> tags)
        # For the inline format: "Name.<br>Name.<br>"
        if not entries:
            # Get raw HTML between h2 and next h2
            raw_entries = []
            sib = h2.next_sibling
            while sib:
                if hasattr(sib, "name") and sib.name == "h2" and "rub" in sib.get("class", []):
                    break
                if hasattr(sib, "name"):
                    raw_entries.append(str(sib))
                elif isinstance(sib, str):
                    raw_entries.append(str(sib))
                sib = sib.next_sibling

            raw = "".join(raw_entries)
            # Split by <br> or <br/>
            parts = re.split(r"<br\s*/?>", raw)
            for part in parts:
                # Strip HTML tags
                text = re.sub(r"<[^>]+>", "", part).strip()
                text = text.replace("\u2013", "-").replace("\u2014", "-")
                if text:
                    entries.append(self._parse_entry(text))

        return entries

    def _parse_entries(self, content_items: list) -> list[dict]:
        """Parse a list of text entries into name/description dicts."""
        result = []
        for item in content_items:
            if isinstance(item, dict):
                result.append(item)
            elif isinstance(item, str) and item.strip():
                entry = self._parse_entry(item.strip())
                if entry:
                    result.append(entry)
        return result

    def _parse_entry(self, text: str) -> dict | None:
        """Parse a single entry text into name/description.

        Formats:
        - 'Nombre.' (just a name, no description - summarized)
        - 'Nombre (X/día).'  (name with usage)
        - 'Nombre. Descripción...' (full description)
        - 'Nombre (recarga X–Y). Descripción...'
        - 'Nombre.Descripción...' (concatenated, no space after period from HTML parsing)
        """
        text = text.strip()
        if not text:
            return None

        # Normalize unicode dashes
        text = self._normalize_dashes(text)

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)

        # Try: period followed by space or end of string
        first_period = re.search(r"\.(?:\s|$)", text)
        if first_period and first_period.start() > 0:
            name = text[:first_period.start()].strip()
            desc = text[first_period.end():].strip()
            if name.endswith(")") and len(desc) == 0:
                return {"name": name, "description": ""}
            return {"name": name, "description": desc}

        # Try: period followed by uppercase letter (concatenated case: "Garras.Tirada...")
        # Skip single-letter matches and number periods (like "1.50")
        first_period = re.search(r"\.(?=[A-ZÁÉÍÓÚÑ])", text)
        if first_period and first_period.start() > 1:
            name = text[:first_period.start()].strip()
            desc = text[first_period.end():].strip()
            # Don't split if we matched inside a parenthetical like "(recarga 5–6)"
            if "(" in name and not name.endswith(")"):
                pass  # Period inside parentheses, skip
            else:
                return {"name": name, "description": desc}

        # Period at very end of text (summarized name only)
        if text.endswith("."):
            name = text[:-1].strip()
            return {"name": name, "description": ""}

        # No period found, whole thing is the name
        return {"name": text, "description": ""}

    def _extract_first_number(self, text: str) -> int:
        """Extract the first integer from text."""
        text = self._normalize_dashes(text)
        match = re.search(r"(\d+)", text)
        if match:
            return int(match.group(1))
        return 0

    def _parse_int(self, text: str) -> int:
        """Parse integer from text, handling unicode minus signs."""
        text = self._normalize_dashes(text.strip())
        try:
            return int(text)
        except ValueError:
            return 0

    @staticmethod
    def _split_csv(text: str) -> list[str]:
        """Split comma-separated values, handling semicolons for mixed types."""
        if not text:
            return []
        items = []
        # Split by both comma and semicolon
        for part in re.split(r"[;,]", text):
            item = part.strip()
            if item:
                items.append(item)
        return items
