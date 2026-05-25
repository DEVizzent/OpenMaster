import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.parser import parse_items, MagicItem
from src.search import SearchEngine
from src.treasure import (
    TreasureGenerator,
    random_gem,
    random_art_object,
    random_mundane_item,
    TREASURE_VALUES,
)

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


def _pick_random_item(rarity: str) -> dict[str, Any] | None:
    try:
        items = engine.random_by_rarity(rarity, 1)
        if items:
            return dict(items[0])
    except ValueError:
        pass
    return None


treasure_gen = TreasureGenerator(random_item_func=_pick_random_item)


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


def _format_treasure_result(result: dict[str, Any]) -> str:
    lines = [f"Tesoro generado para nivel {result['nivel']}"]
    if result.get("tesoro_mayor"):
        lines[0] += " [TESORO MAYOR]"
    lines.append("")

    coins = result.get("monedas", [])
    if coins:
        lines.append("── Monedas ──────────────")
        for c in coins:
            coin_type = c.get("coin_name", "")
            value = c.get("result", 0)
            abbrev = c.get("coin_abbrev", "")
            lines.append(f"  {c['detail']} → {value} {abbrev} ({coin_type})")
        total_gp_coins = sum(c.get("total_gp", 0) for c in coins)
        lines.append(f"  → {total_gp_coins:.0f} po en monedas\n")

    goods = result.get("bienes", [])
    if goods:
        lines.append("── Bienes ───────────────")
        for g in goods:
            if g.get("nombre"):
                lines.append(f"    • {g['nombre']} ({g['valor']} po)")
        lines.append("")

    magic_items = result.get("objetos_magicos", [])
    mundanes = [m for m in magic_items if not m.get("rareza_origen")]
    real_magics = [m for m in magic_items if m.get("rareza_origen")]

    if real_magics:
        lines.append("── Objetos mágicos ──────")
        for item in real_magics:
            tier_label = {
                "minor": "Menor",
                "medium": "Medio",
                "major": "Mayor",
            }.get(item.get("tier_srd", ""), item.get("tier_srd", ""))
            name = item.get("nombre", f"[{item.get('rareza_origen', '?')}]")
            lines.append(f"  {tier_label} → {name} ({item.get('rareza_origen', '?')})")
        lines.append("")

    total_po = result.get("total_po_estimado", 0)
    lines.append(f"Total estimado: {total_po:.0f} po")

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
        Tool(
            name="generar_tesoro",
            description="Genera un tesoro completo para un encuentro de nivel dado. Incluye monedas, bienes (gemas/arte) y objetos mágicos. Usa tesoro_mayor=True para jefes finales o cofres legendarios (probabilidad y cantidad aumentadas).",
            inputSchema={
                "type": "object",
                "properties": {
                    "nivel": {
                        "type": "integer",
                        "description": "Nivel del encuentro (1-30)",
                        "minimum": 1,
                        "maximum": 30,
                    },
                    "tesoro_mayor": {
                        "type": "boolean",
                        "description": "True para tesoro de jefe/cofre importante (+25 a tiradas y +1 objeto extra)",
                        "default": False,
                    },
                },
                "required": ["nivel"],
            },
        ),
        Tool(
            name="gema_aleatoria",
            description="Genera una gema aleatoria con su valor en po y ejemplos.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="objeto_arte_aleatorio",
            description="Genera un objeto de arte aleatorio con su valor en po y ejemplos.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="objeto_mundano_aleatorio",
            description="Genera un objeto mundano aleatorio (alquímico, armadura, arma o herramienta).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="valor_tesoro_esperado",
            description="Devuelve el valor esperado en po para un encuentro de nivel dado.",
            inputSchema={
                "type": "object",
                "properties": {
                    "nivel": {
                        "type": "integer",
                        "description": "Nivel del encuentro (1-30)",
                        "minimum": 1,
                        "maximum": 30,
                    },
                },
                "required": ["nivel"],
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

    elif name == "generar_tesoro":
        nivel = arguments.get("nivel")
        if not nivel or not 1 <= nivel <= 30:
            return [TextContent(type="text", text="Error: nivel debe ser 1-30.")]
        tesoro_mayor = arguments.get("tesoro_mayor", False)
        result = treasure_gen.generate_full(nivel, tesoro_mayor=tesoro_mayor)
        return [TextContent(type="text", text=_format_treasure_result(result))]

    elif name == "gema_aleatoria":
        gema = random_gem()
        lines = [
            "Gema generada:",
            f"  {gema['nombre']}",
            f"  Valor: {gema['valor']} po",
        ]
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "objeto_arte_aleatorio":
        art = random_art_object()
        lines = [
            "Objeto de arte generado:",
            f"  {art['nombre']}",
            f"  Valor: {art['valor']} po",
        ]
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "objeto_mundano_aleatorio":
        item = random_mundane_item()
        lines = [
            "Objeto mundano generado:",
            f"  {item['nombre']}",
            f"  Categoría: {item['categoria']}",
        ]
        coste = item.get("coste") or item.get("coste_total") or item.get("coste_unitario")
        if coste:
            lines.append(f"  Coste: {coste} po")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "valor_tesoro_esperado":
        nivel = arguments.get("nivel")
        if not nivel or not 1 <= nivel <= 30:
            return [TextContent(type="text", text="Error: nivel debe ser 1-30.")]
        valor = treasure_gen.expected_value(nivel)
        return [TextContent(type="text", text=f"Valor de tesoro esperado para nivel {nivel}: {valor} po")]

    else:
        return [TextContent(type="text", text=f"Error: herramienta desconocida '{name}'.")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
