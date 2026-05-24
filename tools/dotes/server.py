"""MCP server para consultar dotes de D&D 5.5."""

import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from src.models import Feat
from src.service import FeatService

DATA_DIR = Path(__file__).parent / "data"
DOTES_JSON = DATA_DIR / "dotes.json"


def load_feats() -> list[Feat]:
    if DOTES_JSON.exists():
        data = json.loads(DOTES_JSON.read_text(encoding="utf-8"))
        return [Feat.from_dict(d) for d in data]
    return []


def build_server(service: FeatService) -> Server:
    server = Server("dotes-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="buscar_dotes",
                description="Busca dotes cuyo nombre contenga el texto dado (case-insensitive, partial match).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Texto a buscar en el nombre del dote.",
                        }
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="listar_dotes",
                description="Lista dotes aplicando filtros opcionales: categoría, atributo requerido, nivel máximo y búsqueda de texto.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "categoria": {
                            "type": "string",
                            "enum": ["origen", "general", "estilo de combate", "épico"],
                            "description": "Filtrar por categoría del dote.",
                        },
                        "atributo": {
                            "type": "string",
                            "enum": [
                                "Fuerza",
                                "Destreza",
                                "Constitución",
                                "Inteligencia",
                                "Sabiduría",
                                "Carisma",
                            ],
                            "description": "Filtrar por atributo requerido.",
                        },
                        "nivel_max": {
                            "type": "integer",
                            "description": "Filtrar dotes cuyo nivel requerido sea <= a este valor. Dotes sin nivel requerido siempre se incluyen.",
                        },
                        "buscar_texto": {
                            "type": "string",
                            "description": "Buscar texto en el nombre o descripción del dote.",
                        },
                    },
                },
            ),
            Tool(
                name="detalle_dote",
                description="Obtiene la información completa de un dote por su nombre exacto (case-insensitive).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nombre": {
                            "type": "string",
                            "description": "Nombre exacto del dote.",
                        }
                    },
                    "required": ["nombre"],
                },
            ),
            Tool(
                name="listar_categorias",
                description="Devuelve la lista de categorías de dotes disponibles.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "buscar_dotes":
            query = arguments.get("query", "")
            results = service.buscar_dotes(query)
            return [_feats_as_text(results, "buscar_dotes", query=query)]

        elif name == "listar_dotes":
            categoria = arguments.get("categoria")
            atributo = arguments.get("atributo")
            nivel_max = arguments.get("nivel_max")
            buscar_texto = arguments.get("buscar_texto")
            results = service.listar_dotes(
                categoria=categoria,
                atributo=atributo,
                nivel_max=nivel_max,
                buscar_texto=buscar_texto,
            )
            return [
                _feats_as_text(
                    results,
                    "listar_dotes",
                    categoria=categoria,
                    atributo=atributo,
                    nivel_max=nivel_max,
                    buscar_texto=buscar_texto,
                )
            ]

        elif name == "detalle_dote":
            nombre = arguments.get("nombre", "")
            feat = service.detalle_dote(nombre)
            if feat:
                return [TextContent(type="text", text=json.dumps(feat.to_dict(), ensure_ascii=False, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": f"Dote '{nombre}' no encontrado"}, ensure_ascii=False))]

        elif name == "listar_categorias":
            categorias = service.listar_categorias()
            return [TextContent(type="text", text=json.dumps(categorias, ensure_ascii=False))]

        return [TextContent(type="text", text=json.dumps({"error": f"Tool '{name}' no reconocida"}, ensure_ascii=False))]

    return server


def _feats_as_text(feats: list[Feat], tool: str, **filters) -> TextContent:
    active_filters = {k: v for k, v in filters.items() if v}
    filter_info = ", ".join(f"{k}={v}" for k, v in active_filters.items())
    header = f"{tool} ({len(feats)} resultados"
    if filter_info:
        header += f", filtros: {filter_info}"
    header += ")"

    lines = [header + "\n"]
    for f in feats:
        lines.append(f"- **{f.nombre}**  [{f.categoria}]  {f.prerequisitos_raw}")
    return TextContent(type="text", text="\n".join(lines))


def main():
    feats = load_feats()
    service = FeatService(feats)
    server = build_server(service)

    import asyncio
    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write)

    asyncio.run(run())


if __name__ == "__main__":
    main()
