import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.parser import parse_items, MagicItem
from src.search import SearchEngine

ITEMS_PATH = Path(__file__).parent / "items.json"

server = Server("objetos-magicos")


def _load_engine() -> SearchEngine:
    if ITEMS_PATH.exists():
        with open(ITEMS_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    else:
        html_path = Path(__file__).parent / "rawData" / "Objetos Mágicos D&D 5.5.html"
        items = parse_items(html_path)
    return SearchEngine(items)


engine = _load_engine()


def _format_item(item: MagicItem) -> str:
    lines = [
        f"**{item['nombre']}**",
        f"Tipo: {item['tipo']}" + (f" ({item['subtipo']})" if item['subtipo'] else ""),
        f"Rareza: {item['rareza']}",
    ]
    if item["requiere_sintonizacion"]:
        linea = "Requiere sintonización"
        if item["sintonizacion_clase"]:
            linea += f" ({item['sintonizacion_clase']})"
        lines.append(linea)
    if item["descripcion"]:
        lines.append("")
        lines.append(item["descripcion"])
    return "\n".join(lines)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_items",
            description="Buscar objetos mágicos por nombre (búsqueda difusa), tipo, rareza y/o requisito de sintonización. Todos los parámetros son opcionales y se combinan como filtros.",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Parte del nombre del objeto mágico (búsqueda difusa, ej: 'espada', 'anillo de prot')",
                    },
                    "tipo": {
                        "type": "string",
                        "description": "Tipo de objeto: Anillo, Arma, Armadura, Poción, Bastón, Varita, Vara, Objeto maravilloso, Pergamino",
                    },
                    "rareza": {
                        "type": "string",
                        "description": "Rareza: Común, Infrecuente, Raro, Muy raro, Legendario, Artefacto, Rareza variable",
                    },
                    "requiere_sintonizacion": {
                        "type": "boolean",
                        "description": "Si requiere sintonización (true/false)",
                    },
                },
            },
        ),
        Tool(
            name="get_item",
            description="Obtener la descripción completa de un objeto mágico por su nombre. Soporta búsqueda difusa (ej: 'anillo de protecion' encuentra 'Anillo de protección').",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre del objeto mágico (exacto o aproximado)",
                    },
                },
                "required": ["nombre"],
            },
        ),
        Tool(
            name="list_types",
            description="Listar todos los tipos de objetos mágicos disponibles.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_rarities",
            description="Listar todas las rarezas de objetos mágicos disponibles.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "search_items":
        nombre = arguments.get("nombre")
        tipo = arguments.get("tipo")
        rareza = arguments.get("rareza")
        requiere_sintonizacion = arguments.get("requiere_sintonizacion")

        results = engine.search(
            nombre=nombre,
            tipo=tipo,
            rareza=rareza,
            requiere_sintonizacion=requiere_sintonizacion,
        )

        if not results:
            return [TextContent(type="text", text="No se encontraron objetos mágicos con esos criterios.")]

        lines = [f"Se encontraron {len(results)} objeto(s) mágico(s):\n"]
        for item in results:
            lines.append(_format_item(item))
            lines.append("---\n")

        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_item":
        nombre = arguments.get("nombre", "")
        if not nombre:
            return [TextContent(type="text", text="Error: Debes especificar un nombre.")]

        item = engine.get(nombre)
        if item is None:
            return [TextContent(type="text", text=f"No se encontró ningún objeto mágico parecido a '{nombre}'.")]

        return [TextContent(type="text", text=_format_item(item))]

    elif name == "list_types":
        tipos = engine.list_types()
        lines = ["Tipos de objetos mágicos disponibles:"]
        for t in tipos:
            lines.append(f"- {t}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "list_rarities":
        rarezas = engine.list_rarities()
        lines = ["Rarezas de objetos mágicos disponibles:"]
        for r in rarezas:
            lines.append(f"- {r}")
        return [TextContent(type="text", text="\n".join(lines))]

    else:
        return [TextContent(type="text", text=f"Error: herramienta desconocida '{name}'.")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
