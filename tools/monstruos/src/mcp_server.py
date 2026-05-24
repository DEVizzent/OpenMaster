"""
MCP Server for D&D 5.5 Monster Lookup.

Provides tools for searching, filtering, and retrieving monster data
from a local database parsed from aidedd.org.
"""
import json
import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.monster_parser import MonsterParser
from src.monster_db import MonsterDB

DATA_FILE = Path(__file__).parent.parent / "monster_data.json"
HTML_FILE = Path(__file__).parent.parent / "rawData" / "Monstruos D&D 5.5.html"
ENRICHMENT_FILE = Path(__file__).parent.parent / "rawData" / "monster_enrichment.json"

server = Server("monstruos-mcp")
db: MonsterDB | None = None


def get_db() -> MonsterDB:
    """Load or return cached database."""
    global db
    if db is not None:
        return db

    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            monsters = json.load(f)
    else:
        parser = MonsterParser()
        enrichment = str(ENRICHMENT_FILE) if ENRICHMENT_FILE.exists() else None
        monsters = parser.parse_file(str(HTML_FILE), enrichment)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(monsters, f, ensure_ascii=False, indent=2)

    db = MonsterDB(monsters)
    return db


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_monsters",
            description="Busca monstruos por nombre (búsqueda parcial, insensible a acentos/mayúsculas). Devuelve lista con nombre, tipo, VD, tamaño y alineamiento.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texto a buscar en el nombre del monstruo (ej: 'dragón', 'zombi', 'águila').",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número máximo de resultados (default: 20).",
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_monster",
            description="Obtiene la ficha completa de un monstruo: atributos, CA, PG, velocidad, inmunidades, resistencias, sentidos, idiomas, rasgos, acciones, acciones legendarias, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nombre exacto del monstruo (ej: 'Aboleth', 'Dragón rojo joven', 'Zombi').",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="filter_monsters",
            description="Filtra monstruos por tipo, VD (CR), tamaño, alineamiento, hábitat y si es legendario. Todos los parámetros son opcionales.",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Tipo de monstruo (ej: 'Dragón', 'Muerto viviente', 'Bestia', 'Infernal', 'Aberración').",
                    },
                    "subtype": {
                        "type": "string",
                        "description": "Subtipo (ej: 'demonio', 'dinosaurio', 'titan', 'mago').",
                    },
                    "cr_min": {
                        "type": "number",
                        "description": "VD mínimo (ej: 0, 0.25, 5, 10).",
                    },
                    "cr_max": {
                        "type": "number",
                        "description": "VD máximo (ej: 5, 10, 20, 30).",
                    },
                    "size": {
                        "type": "string",
                        "description": "Tamaño (ej: 'Diminuto', 'Pequeño', 'Mediano', 'Grande', 'Enorme', 'Gargantuesco').",
                    },
                    "alignment": {
                        "type": "string",
                        "description": "Alineamiento (ej: 'caótico malvado', 'legal bueno', 'neutral', 'sin alineamiento').",
                    },
                    "habitat": {
                        "type": "string",
                        "description": "Hábitat (ej: 'Forest', 'Swamp', 'Mountain', 'Underdark', 'Any').",
                    },
                    "legendary": {
                        "type": "boolean",
                        "description": "Si es true, solo monstruos legendarios. Si es false, solo no legendarios.",
                    },
                },
            },
        ),
        Tool(
            name="list_types",
            description="Lista todos los tipos de monstruos disponibles.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_sizes",
            description="Lista todos los tamaños de monstruos disponibles.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_alignments",
            description="Lista todos los alineamientos de monstruos disponibles.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_crs",
            description="Lista todos los valores de VD (CR) disponibles con su contador de monstruos.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_habitats",
            description="Lista todos los hábitats disponibles.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_db_stats",
            description="Obtiene estadísticas de la base de datos: número total de monstruos, distribución por tipo, etc.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


def _format_monster_brief(m: dict) -> str:
    """Format a monster summary for output."""
    subtype_str = f" ({m.get('subtype')})" if m.get("subtype") else ""
    legendary_str = " [Legendario]" if m.get("legendary") else ""
    return f"**{m['name']}**{subtype_str} — VD {m['cr']} | {m['type']} {m['size']} | {m['alignment']}{legendary_str}"


def _format_monster_full(m: dict) -> str:
    """Format a full monster stat block as markdown."""
    lines = []

    # Name
    subtype_str = f" ({m.get('subtype')})" if m.get("subtype") else ""
    lines.append(f"# {m['name']}{subtype_str}")
    if m.get("name_en") and m["name_en"] != m["name"]:
        lines.append(f"*{m['name_en']}*")

    lines.append("")
    lines.append(f"**{m['type']} {m['size']}, {m['alignment']}**")

    # Initiative
    if m.get("initiative") is not None:
        lines.append(f"**Iniciativa:** {m['initiative']:+d}")

    # Defense
    lines.append(f"**CA:** {m['ac']}")
    lines.append(f"**PG:** {m['hp']} ({m['hp_formula']})")

    # Speed
    speed_parts = []
    speed = m.get("speed", {})
    if speed.get("walk"):
        speed_parts.append(f"{speed['walk']} m")
    if speed.get("fly"):
        speed_parts.append(f"volar {speed['fly']} m")
    if speed.get("swim"):
        speed_parts.append(f"nadar {speed['swim']} m")
    if speed.get("climb"):
        speed_parts.append(f"trepar {speed['climb']} m")
    if speed.get("burrow"):
        speed_parts.append(f"excavar {speed['burrow']} m")
    lines.append(f"**Velocidad:** {', '.join(speed_parts) if speed_parts else '—'}")

    # Attributes table
    lines.append("")
    lines.append("| | FUE | DES | CON | INT | SAB | CAR |")
    lines.append("|--|-----|-----|-----|-----|-----|-----|")
    attrs = m.get("attributes", {})
    vals = "| **Valor** |"
    mods = "| **Mod** |"
    saves = "| **Salv** |"
    for stat in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        a = attrs.get(stat, {})
        vals += f" {a.get('value', '—')} |"
        mods += f" {a.get('mod', 0):+d} |"
        saves += f" {a.get('save', 0):+d} |"
    lines.append(vals)
    lines.append(mods)
    lines.append(saves)

    # Skills
    if m.get("skills"):
        skills = ", ".join(f"{k} {v:+d}" for k, v in m["skills"].items())
        lines.append(f"\n**Habilidades:** {skills}")

    # Vulnerabilities / Resistances / Immunities
    for label, key in [
        ("Vulnerabilidades", "vulnerabilities"),
        ("Resistencias", "resistances"),
        ("Inmunidades", "immunities"),
    ]:
        if m.get(key):
            lines.append(f"**{label}:** {', '.join(m[key])}")

    # Senses
    senses = m.get("senses", {})
    sense_parts = []
    if senses.get("darkvision"):
        sense_parts.append(f"visión en la oscuridad {senses['darkvision']} m")
    if senses.get("blindsight"):
        sense_parts.append(f"visión ciega {senses['blindsight']} m")
    if senses.get("truesight"):
        sense_parts.append(f"visión verdadera {senses['truesight']} m")
    if senses.get("tremorsense"):
        sense_parts.append(f"sentir vibraciones {senses['tremorsense']} m")
    if senses.get("pasiva"):
        sense_parts.append(f"Percepción pasiva {senses['pasiva']}")
    if sense_parts:
        lines.append(f"**Sentidos:** {', '.join(sense_parts)}")

    # Languages
    if m.get("languages"):
        lines.append(f"**Idiomas:** {m['languages']}")
    elif m.get("languages") == "":
        lines.append("**Idiomas:** —")

    # CR
    lines.append(f"**VD:** {m['cr']} (PX {m['xp']}; BC +{m['bc']})")

    # Equipment
    if m.get("equipment"):
        lines.append(f"**Equipamiento:** {', '.join(m['equipment'])}")

    # Traits
    if m.get("traits"):
        lines.append("\n## Atributos")
        for t in m["traits"]:
            name = t.get("name", "")
            desc = t.get("description", "")
            if desc:
                lines.append(f"***{name}.*** {desc}")
            else:
                lines.append(f"*{name}*")

    # Actions
    if m.get("actions"):
        lines.append("\n## Acciones")
        for a in m["actions"]:
            name = a.get("name", "")
            desc = a.get("description", "")
            if desc:
                lines.append(f"***{name}.*** {desc}")
            else:
                lines.append(f"*{name}*")

    # Bonus Actions
    if m.get("bonus_actions"):
        lines.append("\n## Acciones Bonus")
        for a in m["bonus_actions"]:
            name = a.get("name", "")
            desc = a.get("description", "")
            if desc:
                lines.append(f"***{name}.*** {desc}")
            else:
                lines.append(f"*{name}*")

    # Reactions
    if m.get("reactions"):
        lines.append("\n## Reacciones")
        for r in m["reactions"]:
            name = r.get("name", "")
            desc = r.get("description", "")
            if desc:
                lines.append(f"***{name}.*** {desc}")
            else:
                lines.append(f"*{name}*")

    # Legendary
    if m.get("legendary_resistances", 0) > 0:
        lines.append(f"\n**Resistencias legendarias:** {m['legendary_resistances']}/día")
    if m.get("legendary_actions"):
        lines.append("\n## Acciones Legendarias")
        for la in m["legendary_actions"]:
            name = la.get("name", "")
            desc = la.get("description", "")
            if desc:
                lines.append(f"***{name}.*** {desc}")
            else:
                lines.append(f"*{name}*")

    # Habitat & Source
    if m.get("habitat"):
        lines.append(f"\n**Hábitat:** {', '.join(m['habitat'])}")
    if m.get("source"):
        lines.append(f"**Fuente:** {m['source']}")

    return "\n".join(lines)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    database = get_db()

    try:
        if name == "search_monsters":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)
            results = database.search(query, limit=limit)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No se encontraron monstruos para: **{query}**",
                )]

            lines = [f"## Resultados para: **{query}** ({len(results)} encontrados)\n"]
            for r in results:
                lines.append(f"- {_format_monster_brief(r)}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_monster":
            name_query = arguments.get("name", "")
            monster = database.get_monster(name_query)

            if not monster:
                return [TextContent(
                    type="text",
                    text=f"No se encontró el monstruo: **{name_query}**. Prueba a buscar con `search_monsters`.",
                )]

            return [TextContent(type="text", text=_format_monster_full(monster))]

        elif name == "filter_monsters":
            kwargs = {
                "type": arguments.get("type"),
                "subtype": arguments.get("subtype"),
                "cr_min": arguments.get("cr_min"),
                "cr_max": arguments.get("cr_max"),
                "size": arguments.get("size"),
                "alignment": arguments.get("alignment"),
                "habitat": arguments.get("habitat"),
                "legendary": arguments.get("legendary"),
            }
            # Remove None values
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            results = database.filter_monsters(**kwargs)

            # Build description of filters applied
            filter_desc = []
            for k, v in kwargs.items():
                filter_desc.append(f"{k}={v}")
            filter_str = ", ".join(filter_desc) if filter_desc else "sin filtros"

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No se encontraron monstruos con filtros: {filter_str}",
                )]

            lines = [f"## Monstruos filtrados ({len(results)} resultados)\nFiltros: {filter_str}\n"]
            for r in results:
                lines.append(f"- {_format_monster_brief(r)}")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "list_types":
            types = database.list_types()
            lines = ["## Tipos de monstruos disponibles\n"]
            for t in types:
                count = len(database.filter_monsters(type=t))
                lines.append(f"- **{t}** ({count})")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "list_sizes":
            sizes = database.list_sizes()
            lines = ["## Tamaños disponibles\n"]
            for s in sizes:
                count = len(database.filter_monsters(size=s))
                lines.append(f"- **{s}** ({count})")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "list_alignments":
            alignments = database.list_alignments()
            lines = ["## Alineamientos disponibles\n"]
            for a in alignments:
                count = len(database.filter_monsters(alignment=a))
                lines.append(f"- **{a}** ({count})")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "list_crs":
            crs = database.list_crs()
            lines = ["## Valores de VD (CR) disponibles\n"]
            for cr in crs:
                count = len(database.filter_monsters(cr_min=database._cr_sort_key(cr), cr_max=database._cr_sort_key(cr)))
                lines.append(f"- **VD {cr}** ({count} monstruos)")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "list_habitats":
            habitats = database.list_habitats()
            lines = ["## Hábitats disponibles\n"]
            for h in habitats:
                count = len(database.filter_monsters(habitat=h))
                lines.append(f"- **{h}** ({count})")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "get_db_stats":
            total = database.count()
            types = database.list_types()
            lines = [
                f"## Estadísticas de la base de datos",
                f"",
                f"**Total de monstruos:** {total}",
                f"**Tipos de monstruo:** {len(types)}",
                f"",
                f"### Distribución por tipo:",
            ]
            for t in types:
                count = len(database.filter_monsters(type=t))
                pct = f"{(count / total * 100):.1f}%" if total else "0%"
                lines.append(f"- {t}: {count} ({pct})")

            legendary = len(database.filter_monsters(legendary=True))
            lines.append(f"\n**Monstruos legendarios:** {legendary}")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            return [TextContent(type="text", text=f"Herramienta desconocida: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
