from mcp.server.fastmcp import FastMCP
from viajes_mcp.core import should_encounter, roll_encounter_type

mcp = FastMCP("Viajes Encounters")


@mcp.tool()
def roll_encounter(rhythm: str, danger_level: str, boost: str = "neutral") -> str:
    """Roll for a travel encounter during a journey leg (1 day or 1 night camp).

    Args:
        rhythm: Travel pace — "fast" (40%% chance), "normal" (60%%), or "lively" (80%%)
        danger_level: Zone danger — "low", "medium", "high", or "lethal"
        boost: Group tactics modifier — "positive" (safer), "neutral", or "negative" (riskier)
    """
    if not should_encounter(rhythm):
        return "none"
    return roll_encounter_type(danger_level, boost)


if __name__ == "__main__":
    mcp.run(transport="stdio")
