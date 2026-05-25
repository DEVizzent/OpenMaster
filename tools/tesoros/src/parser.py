import re
from pathlib import Path
from typing import TypedDict


class MagicItem(TypedDict):
    nombre: str
    tipo: str
    subtipo: str | None
    rareza: str
    requiere_sintonizacion: bool
    sintonizacion_clase: str | None
    descripcion: str
    es_ogl: bool
    traducido: bool
    nombre_en: str | None


KNOWN_TYPES = [
    "Armadura",
    "Arma",
    "Anillo",
    "Poción",
    "Bastón",
    "Varita",
    "Vara",
    "Objeto maravilloso",
    "Pergamino",
]

NON_OGL_MARKER = "Description not available (not OGL)"
NON_OGL_HTML = '<p class="resume">Description not available (not OGL).</p>'


def parse_items(html_path: Path) -> list[MagicItem]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    items: list[MagicItem] = []

    for bloc in soup.find_all("div", class_="bloc"):
        h1 = bloc.find("h1")
        if not h1:
            continue

        nombre = h1.get_text(strip=True)

        prerequis_div = bloc.find("div", class_="prerequis")
        prerequis = prerequis_div.get_text(strip=True) if prerequis_div else ""

        parsed = _parse_prerequis(prerequis)

        description_div = bloc.find("div", class_="description")
        resume_p = bloc.find("p", class_="resume")

        if description_div:
            # Get inner HTML to preserve rich text structure
            descripcion = "".join(
                str(child) for child in description_div.children
            ).strip()
            # Convert <br>, <br/>, <br /> to newlines for readability
            descripcion = re.sub(r"<br\s*/?>", "\n", descripcion)
            # Strip remaining HTML tags
            descripcion = re.sub(r"<[^>]+>", "", descripcion)
            # Collapse multiple newlines
            descripcion = re.sub(r"\n\s*\n", "\n", descripcion)
            # Unescape HTML entities
            descripcion = descripcion.replace("&nbsp;", " ")
            es_ogl = True
        elif resume_p:
            descripcion = NON_OGL_MARKER
            es_ogl = False
        else:
            descripcion = ""
            es_ogl = True

        items.append({
            "nombre": nombre,
            "tipo": parsed["tipo"],
            "subtipo": parsed["subtipo"],
            "rareza": parsed["rareza"],
            "requiere_sintonizacion": parsed["requiere_sintonizacion"],
            "sintonizacion_clase": parsed["sintonizacion_clase"],
            "descripcion": descripcion,
            "es_ogl": es_ogl,
            "traducido": False,
            "nombre_en": None,
        })

    return items


def _parse_prerequis(prerequis: str) -> dict:
    prerequis = prerequis.strip()

    tipo = _extract_type(prerequis)
    rest = prerequis[len(tipo):].lstrip()

    subtipo = None
    if rest.startswith("("):
        subtipo, rest = _extract_parenthetical(rest)

    # Remove leading ", " after type(+subtype)
    if rest.startswith(", "):
        rest = rest[2:]

    rareza_part = rest.strip()

    requiere_sintonizacion, sintonizacion_clase, rareza_part = _extract_attunement(rareza_part)

    rareza = _normalize_rarity(rareza_part)

    return {
        "tipo": tipo,
        "subtipo": subtipo,
        "rareza": rareza,
        "requiere_sintonizacion": requiere_sintonizacion,
        "sintonizacion_clase": sintonizacion_clase,
    }


def _extract_type(text: str) -> str:
    for t in sorted(KNOWN_TYPES, key=len, reverse=True):
        if text.startswith(t):
            return t
    # Fallback: take first word before comma or parenthesis
    match = re.match(r"^([^(,]+)", text)
    return match.group(1).strip() if match else text


def _extract_parenthetical(text: str) -> tuple[str, str]:
    """Extract content from first parenthetical group. Returns (content, rest)."""
    if not text.startswith("("):
        return "", text

    depth = 0
    for i, c in enumerate(text):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[1:i], text[i + 1:]

    return text[1:], ""


def _extract_attunement(rareza_part: str) -> tuple[bool, str | None, str]:
    """Extract attunement info from rarity part. Returns (requires, class, cleaned_rarity)."""
    pattern = r'\s*\(requiere sintonización(?:\s*(?:con(?:\s*un)?\s*(.+?)))?\)'
    match = re.search(pattern, rareza_part, re.IGNORECASE)

    if not match:
        return False, None, rareza_part

    sintonizacion_clase = None
    if match.group(1):
        sintonizacion_clase = match.group(1).strip().lower()

    cleaned = re.sub(pattern, "", rareza_part, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip(",").strip()

    return True, sintonizacion_clase, cleaned


def _normalize_rarity(rareza: str) -> str:
    """Capitalize rarity words properly, handling multi-tier and parenthetical rarities."""
    rareza = rareza.strip().lower()

    if not rareza:
        return rareza

    if "rareza variable" in rareza:
        return "Rareza variable"

    # Capitalize first letter
    rareza = rareza[0].upper() + rareza[1:]

    # Find top-level " o " and ", " delimiters (not inside parentheses)
    depth = 0
    positions: list[int] = []
    i = 0
    while i < len(rareza):
        c = rareza[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0:
            if rareza[i:i+3] == " o ":
                positions.append(i + 3)
                i += 2
            elif rareza[i:i+2] == ", ":
                positions.append(i + 2)
                i += 1
        i += 1

    result = list(rareza)
    for pos in reversed(positions):
        if pos < len(result) and result[pos].isalpha():
            result[pos] = result[pos].upper()

    return "".join(result)
