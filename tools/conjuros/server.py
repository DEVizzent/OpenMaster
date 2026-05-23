"""MCP Server para consulta de conjuros D&D 5.5."""

import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.spellbook import Spellbook, BuscarResult, ListarResult


DATA_PATH = Path(__file__).parent / "data" / "conjuros.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    spellbook = Spellbook(json.load(f))

server = Server("conjuros-mcp")


def _format_tabla(spells: list[dict], incluir_descripcion: bool = False) -> str:
    """Formatea una lista de conjuros en formato tabular."""
    if not spells:
        return "0 resultados."

    headers = ["Nombre", "VO", "Nvl", "Escuela", "Clases", "Tiempo", "Alcance", "Duración", "Conc", "Rit"]
    rows = []
    for s in spells:
        row = [
            s["nombre"],
            s["vo"],
            str(s["nivel"]),
            s["escuela"],
            ", ".join(s["clases"]),
            s["tiempo"],
            s["alcance"],
            s["duracion"],
            "Sí" if s["concentracion"] else "No",
            "Sí" if s["ritual"] else "No",
        ]
        rows.append(row)

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(val))

    # Build table
    fmt = " | ".join(f"{{:<{w}}}" for w in col_widths)
    lines = [fmt.format(*headers)]
    lines.append("-+-".join("-" * w for w in col_widths))
    for row in rows:
        lines.append(fmt.format(*row))

    if incluir_descripcion and len(spells) == 1:
        s = spells[0]
        lines.append("")
        lines.append(f"Descripción: {s['descripcion']}")
        if s.get("niveles_superiores"):
            lines.append(f"A niveles superiores: {s['niveles_superiores']}")

    return "\n".join(lines)


def _format_candidatos(result: BuscarResult) -> str:
    """Formatea resultado de búsqueda con candidatos."""
    if result.conjuro:
        return _format_tabla([result.conjuro], incluir_descripcion=True)
    if result.candidatos:
        lines = [_format_tabla(result.candidatos)]
        lines.append(f"---\n{len(result.candidatos)} resultados. Usa el nombre exacto para ver la descripción.")
        return "\n".join(lines)
    return "No se encontró ningún conjuro con ese nombre."


def _format_listado(result: ListarResult) -> str:
    """Formatea resultado de listado con paginación."""
    if result.total == 0:
        return "0 resultados con esos filtros."

    lines = [_format_tabla(result.conjuros)]

    footer = f"---\nPágina {result.pagina_actual}/{result.total_paginas}"
    footer += f" | {len(result.conjuros)} de {result.total} conjuros"
    if result.total_paginas > 1:
        footer += f". Usa 'pagina={result.pagina_actual + 1}' para ver más."
    lines.append(footer)
    return "\n".join(lines)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="buscar_conjuro",
            description="Busca un conjuro de D&D 5.5 por nombre (búsqueda difusa). "
                        "Devuelve la ficha completa si hay un match claro, o una lista de candidatos si hay varios.",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre del conjuro a buscar (acepta búsqueda aproximada).",
                    },
                },
                "required": ["nombre"],
            },
        ),
        Tool(
            name="listar_conjuros",
            description="Lista conjuros de D&D 5.5 filtrando por nivel, escuela, clase, ritual y/o concentración. "
                        "Requiere al menos un filtro. Paginado (50 por página por defecto).",
            inputSchema={
                "type": "object",
                "properties": {
                    "nivel": {
                        "type": "integer",
                        "description": "Nivel del conjuro (0-9). 0 = trucos.",
                    },
                    "escuela": {
                        "type": "string",
                        "description": "Escuela de magia (Abjuración, Conjuración, Adivinación, "
                                       "Encantamiento, Evocación, Ilusionismo, Nigromancia, Transmutación).",
                    },
                    "clase": {
                        "type": "string",
                        "description": "Clase (bardo, clérigo, druida, paladín, explorador, hechicero, brujo, mago).",
                    },
                    "ritual": {
                        "type": "boolean",
                        "description": "Filtrar por conjuros rituales.",
                    },
                    "concentracion": {
                        "type": "boolean",
                        "description": "Filtrar por conjuros de concentración.",
                    },
                    "pagina": {
                        "type": "integer",
                        "description": "Número de página (empieza en 1).",
                    },
                },
            },
        ),
        Tool(
            name="info_escuelas",
            description="Lista las 8 escuelas de magia con su descripción.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "buscar_conjuro":
        nombre = arguments.get("nombre", "")
        result = spellbook.buscar(nombre)
        output = _format_candidatos(result)
        return [TextContent(type="text", text=output)]

    elif name == "listar_conjuros":
        nivel = arguments.get("nivel")
        escuela = arguments.get("escuela")
        clase = arguments.get("clase")
        ritual = arguments.get("ritual")
        concentracion = arguments.get("concentracion")
        pagina = arguments.get("pagina", 1)

        try:
            result = spellbook.listar(
                nivel=nivel,
                escuela=escuela,
                clase=clase,
                ritual=ritual,
                concentracion=concentracion,
                pagina=pagina,
                por_pagina=50,
            )
        except ValueError as e:
            return [TextContent(type="text", text=str(e))]

        output = _format_listado(result)
        return [TextContent(type="text", text=output)]

    elif name == "info_escuelas":
        escuelas = spellbook.escuelas()
        headers = ["Escuela", "Descripción"]
        col_w = len(headers[0])
        for e in escuelas:
            col_w = max(col_w, len(e["nombre"]))
        rows = [f"{'Escuela':<{col_w}} | Descripción",
                f"{'-'*col_w}-+{'-'*70}"]
        for e in escuelas:
            rows.append(f"{e['nombre']:<{col_w}} | {e['descripcion']}")
        return [TextContent(type="text", text="\n".join(rows))]

    return [TextContent(type="text", text=f"Tool desconocida: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
