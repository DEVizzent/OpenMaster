"""Parse HTML de conjuros D&D 5.5 a JSON estructurado."""

import json
import re
import html as html_mod
from pathlib import Path
from bs4 import BeautifulSoup


ROOT = Path(__file__).parent.parent
HTML_PATH = ROOT / "rawData" / "Conjuros D&D 5.5.html"
TABLE_PATH = ROOT / "rawData" / "table_vo.txt"
OUTPUT_PATH = ROOT / "data" / "conjuros.json"

ESCUELAS = [
    "Abjuración", "Conjuración", "Adivinación", "Encantamiento",
    "Evocación", "Ilusionismo", "Nigromancia", "Transmutación",
]
CLASES_VALIDAS = {"bardo", "clérigo", "druida", "paladín", "explorador", "hechicero", "brujo", "mago"}
SCHOOLS_PATTERN = "|".join(ESCUELAS)


def decode_text(text: str) -> str:
    """Decodifica entidades HTML y limpia."""
    text = html_mod.unescape(text)
    text = text.replace("\xa0", " ").replace("\n", " ").replace("\r", " ")
    return text.strip()


def parse_school_level_classes(ecole_text: str) -> tuple[str, int, list[str]]:
    """Extrae escuela, nivel y clases de 'Transmutación de nivel 2 (bardo, hechicero, mago)'."""
    text = decode_text(ecole_text)
    m = re.match(r"(.+?) de nivel (\d+)\s*\(([^)]+)\)", text)
    if not m:
        raise ValueError(f"No se pudo parsear ecole: {text!r}")
    escuela = m.group(1).strip()
    nivel = int(m.group(2))
    clases_str = m.group(3).strip()
    clases_raw = [c.strip() for c in clases_str.split(",")]
    clases = []
    for c in clases_raw:
        c_lower = c.lower()
        if c_lower in CLASES_VALIDAS:
            clases.append(c_lower)
        else:
            clases.append(c_lower)
    if not clases:
        clases = [c.strip().lower() for c in clases_str.split(",")]
    return escuela, nivel, clases


def parse_duration(duracion_raw: str) -> tuple[str, bool]:
    """Extrae duración limpia y si tiene concentración."""
    text = decode_text(duracion_raw)
    concentracion = False
    clean = text
    m = re.match(r"Concentración,\s*(.+)", text)
    if m:
        concentracion = True
        clean = m.group(1).strip()
    return clean, concentracion


def parse_ritual(tiempo_raw: str) -> tuple[str, bool]:
    """Extrae tiempo limpio y detecta si es ritual."""
    text = decode_text(tiempo_raw)
    ritual = False
    clean = text
    if "ritual" in text.lower():
        ritual = True
    return clean, ritual


def split_description(raw: str) -> tuple[str, str]:
    """Separa descripción y 'A niveles superiores'."""
    text = decode_text(raw)
    # Remove HTML tags but keep br as newlines
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    desc = text
    ns = ""

    # Patterns for "A niveles superiores" / "Mejora de truco"
    patterns = [
        r"\nA niveles superiores[.:]\s*",
        r"\nMejora de truco[.:]\s*",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            desc = text[:m.start()].strip()
            ns = text[m.start():].strip()
            if ns.startswith("A niveles superiores."):
                ns = ns[len("A niveles superiores."):].strip()
            elif ns.startswith("Mejora de truco."):
                ns = ns[len("Mejora de truco."):].strip()
            break

    return desc.strip(), ns.strip()


def load_vo_mapping(table_path: Path, names: list[str]) -> dict[str, str]:
    """Extrae mapeo nombre → VO desde texto de tabla, usando búsqueda secuencial."""
    if not table_path.exists():
        print(f"  [WARN] No se encontró {table_path}, VO quedarán vacíos.")
        return {}

    with open(table_path, "r", encoding="utf-8") as f:
        text = f.read()

    vo_map = {}
    entry_pattern = re.compile(
        r"^ ?EN FR([A-Za-z/' \-]+?)(\d)(" + SCHOOLS_PATTERN + r")"
    )
    entry_no_fr_pattern = re.compile(
        r"^([A-Za-z/' \-]+?)(\d)(" + SCHOOLS_PATTERN + r")"
    )

    last_end = 0
    for name in names:
        idx = text.find(name, last_end)
        if idx < 0:
            # Try case-insensitive
            remaining = text[last_end:]
            idx_lower = remaining.lower().find(name.lower())
            if idx_lower >= 0:
                idx = last_end + idx_lower
            else:
                continue

        after = text[idx + len(name):]
        m = entry_pattern.match(after)
        if not m:
            m = entry_no_fr_pattern.match(after)

        if m:
            vo = m.group(1).strip().rstrip(",")
            vo_map[name] = vo
            last_end = idx + len(name)
        else:
            last_end = idx + 1

    return vo_map


def parse_html(html_path: Path, table_path: Path) -> list[dict]:
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    spells = []
    names_order = []
    for bloc in soup.find_all("div", class_="bloc"):
        h1 = bloc.find("h1")
        if not h1:
            continue
        nombre = decode_text(h1.get_text(strip=True))

        # School, level, classes
        ecole_div = bloc.find("div", class_="ecole")
        if not ecole_div:
            continue
        escuela, nivel, clases = parse_school_level_classes(ecole_div.get_text(strip=True))

        # Casting time
        t_div = bloc.find("div", class_="t")
        tiempo_raw = ""
        if t_div:
            strong = t_div.find("strong")
            if strong:
                strong.decompose()
            tiempo_raw = t_div.get_text(strip=True).lstrip(":").strip()
        tiempo, ritual = parse_ritual(tiempo_raw)

        # Range
        r_div = bloc.find("div", class_="r")
        alcance = ""
        if r_div:
            strong = r_div.find("strong")
            if strong:
                strong.decompose()
            alcance = r_div.get_text(strip=True).lstrip(":").strip()

        # Components
        c_div = bloc.find("div", class_="c")
        componentes = ""
        if c_div:
            strong = c_div.find("strong")
            if strong:
                strong.decompose()
            componentes = c_div.get_text(strip=True).lstrip(":").strip()

        # Duration
        d_div = bloc.find("div", class_="d")
        duracion_raw = ""
        if d_div:
            strong = d_div.find("strong")
            if strong:
                strong.decompose()
            duracion_raw = d_div.get_text(strip=True).lstrip(":").strip()
        duracion, concentracion = parse_duration(duracion_raw)

        # Description
        desc_div = bloc.find("div", class_="description")
        if not desc_div:
            desc_div = bloc.find("p", class_="resume")
        if not desc_div:
            desc_div = bloc.find("div", class_="resume")
        desc_html = str(desc_div) if desc_div else ""
        descripcion, niveles_superiores = split_description(desc_html)

        # Decode all fields (VO will be filled later)
        fields = {
            "nombre": decode_text(nombre),
            "vo": "",
            "nivel": nivel,
            "escuela": decode_text(escuela),
            "clases": clases,
            "tiempo": decode_text(tiempo),
            "alcance": decode_text(alcance),
            "componentes": decode_text(componentes),
            "duracion": decode_text(duracion),
            "concentracion": concentracion,
            "ritual": ritual,
            "fuente": "Player's Handbook 2024",
            "descripcion": decode_text(descripcion),
            "niveles_superiores": decode_text(niveles_superiores),
        }

        spells.append(fields)
        names_order.append(fields["nombre"])

    # Load VO mapping using original order
    vo_map = load_vo_mapping(table_path, names_order)
    for s in spells:
        s["vo"] = vo_map.get(s["nombre"], "")

    # Sort by name for consistency
    spells.sort(key=lambda s: s["nombre"].lower())

    return spells


def main():
    print(f"Parseando {HTML_PATH}...")
    spells = parse_html(HTML_PATH, TABLE_PATH)
    print(f"Extraídos {len(spells)} conjuros.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(spells, f, ensure_ascii=False, indent=2)

    print(f"Guardado en {OUTPUT_PATH}")

    # Stats
    if spells:
        levels = {}
        for s in spells:
            levels[s["nivel"]] = levels.get(s["nivel"], 0) + 1
        print("Distribución por nivel:")
        for lvl in sorted(levels):
            print(f"  Nivel {lvl}: {levels[lvl]}")

        sin_vo = sum(1 for s in spells if not s["vo"])
        print(f"Conjuros sin VO: {sin_vo}")

        rituales = sum(1 for s in spells if s["ritual"])
        print(f"Rituales: {rituales}")


if __name__ == "__main__":
    main()
