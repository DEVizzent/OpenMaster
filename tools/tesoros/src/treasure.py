import random
import re
from typing import Any


COIN_NAMES = {
    "cp": "pc (cobre)",
    "sp": "pp (plata)",
    "gp": "po (oro)",
    "pp": "pt (platino)",
}

COIN_ABBREV = {
    "cp": "pc",
    "sp": "pp",
    "gp": "po",
    "pp": "pt",
}

COIN_VALUE_IN_GP = {
    "cp": 0.01,
    "sp": 0.1,
    "gp": 1,
    "pp": 10,
}

RARITY_MAP = {
    "minor":  {1: "Común", 5: "Infrecuente", 9: "Infrecuente", 13: "Raro", 17: "Raro", 21: "Muy raro"},
    "medium": {6: "Raro", 9: "Raro", 11: "Muy raro", 13: "Muy raro", 17: "Muy raro", 21: "Legendario"},
    "major":  {10: "Muy raro", 13: "Legendario", 15: "Legendario", 17: "Legendario", 20: "Artefacto", 21: "Artefacto"},
}

RARITY_FALLBACK = ["Artefacto", "Legendario", "Muy raro", "Raro", "Infrecuente", "Común"]

SRD_TIERS = ["minor", "medium", "major"]

TREASURE_VALUES = {
    1: 300, 2: 600, 3: 900, 4: 1200, 5: 1600,
    6: 2000, 7: 2600, 8: 3400, 9: 4500, 10: 5800,
    11: 7500, 12: 9800, 13: 13000, 14: 17000, 15: 22000,
    16: 28000, 17: 36000, 18: 47000, 19: 61000, 20: 80000,
}

TREASURE_TABLE: dict[int, dict[str, list[dict[str, Any]]]] = {
    1: {
        "coins": [
            (1, 14, None),
            (15, 29, "1d6 x 1,000 cp"),
            (30, 52, "1d8 x 100 sp"),
            (53, 95, "2d8 x 10 gp"),
            (96, 100, "1d4 x 10 pp"),
        ],
        "goods": [
            (1, 90, None),
            (91, 95, "1 gem"),
            (96, 100, "1 art"),
        ],
        "items": [
            (1, 71, None),
            (72, 95, "1 mundane"),
            (96, 100, "1 minor"),
        ],
    },
    2: {
        "coins": [
            (1, 13, None),
            (14, 23, "1d10 x 1,000 cp"),
            (24, 43, "2d10 x 100 sp"),
            (44, 95, "4d10 x 10 gp"),
            (96, 100, "2d8 x 10 pp"),
        ],
        "goods": [
            (1, 81, None),
            (82, 95, "1d3 gems"),
            (96, 100, "1d3 art"),
        ],
        "items": [
            (1, 49, None),
            (50, 85, "1 mundane"),
            (86, 100, "1 minor"),
        ],
    },
    3: {
        "coins": [
            (1, 11, None),
            (12, 21, "2d10 x 1,000 cp"),
            (22, 41, "4d8 x 100 sp"),
            (42, 95, "1d4 x 100 gp"),
            (96, 100, "1d10 x 10 pp"),
        ],
        "goods": [
            (1, 77, None),
            (78, 95, "1d3 gems"),
            (96, 100, "1d3 art"),
        ],
        "items": [
            (1, 49, None),
            (50, 79, "1d3 mundane"),
            (80, 100, "1 minor"),
        ],
    },
    4: {
        "coins": [
            (1, 11, None),
            (12, 21, "3d10 x 1,000 cp"),
            (22, 41, "4d12 x 1,000 sp"),
            (42, 95, "1d6 x 100 gp"),
            (96, 100, "1d8 x 10 pp"),
        ],
        "goods": [
            (1, 70, None),
            (71, 95, "1d4 gems"),
            (96, 100, "1d3 art"),
        ],
        "items": [
            (1, 42, None),
            (43, 62, "1d4 mundane"),
            (63, 100, "1 minor"),
        ],
    },
    5: {
        "coins": [
            (1, 10, None),
            (11, 19, "1d4 x 10,000 cp"),
            (20, 38, "1d6 x 1,000 sp"),
            (39, 95, "1d8 x 100 gp"),
            (96, 100, "1d10 x 10 pp"),
        ],
        "goods": [
            (1, 60, None),
            (61, 95, "1d4 gems"),
            (96, 100, "1d4 art"),
        ],
        "items": [
            (1, 57, None),
            (58, 67, "1d4 mundane"),
            (68, 100, "1d3 minor"),
        ],
    },
    6: {
        "coins": [
            (1, 10, None),
            (11, 18, "1d6 x 10,000 cp"),
            (19, 37, "1d8 x 1,000 sp"),
            (38, 95, "1d10 x 100 gp"),
            (96, 100, "1d12 x 10 pp"),
        ],
        "goods": [
            (1, 56, None),
            (57, 92, "1d4 gems"),
            (93, 100, "1d4 art"),
        ],
        "items": [
            (1, 54, None),
            (55, 59, "1d4 mundane"),
            (60, 99, "1d3 minor"),
            (100, 100, "1 medium"),
        ],
    },
    7: {
        "coins": [
            (1, 11, None),
            (12, 18, "1d10 x 10,000 cp"),
            (19, 35, "1d12 x 1,000 sp"),
            (36, 93, "2d6 x 100 gp"),
            (94, 100, "3d4 x 10 pp"),
        ],
        "goods": [
            (1, 48, None),
            (49, 88, "1d4 gems"),
            (89, 100, "1d4 art"),
        ],
        "items": [
            (1, 51, None),
            (52, 97, "1d3 minor"),
            (98, 100, "1 medium"),
        ],
    },
    8: {
        "coins": [
            (1, 10, None),
            (11, 15, "1d12 x 10,000 cp"),
            (16, 29, "2d6 x 1,000 sp"),
            (30, 87, "2d8 x 100 gp"),
            (88, 100, "3d6 x 10 pp"),
        ],
        "goods": [
            (1, 45, None),
            (46, 85, "1d6 gems"),
            (86, 100, "1d4 art"),
        ],
        "items": [
            (1, 48, None),
            (49, 96, "1d4 minor"),
            (97, 100, "1 medium"),
        ],
    },
    9: {
        "coins": [
            (1, 10, None),
            (11, 15, "2d6 x 10,000 cp"),
            (16, 29, "2d8 x 1,000 sp"),
            (30, 85, "5d4 x 100 gp"),
            (86, 100, "2d12 x 10 pp"),
        ],
        "goods": [
            (1, 40, None),
            (41, 80, "1d8 gems"),
            (81, 100, "1d4 art"),
        ],
        "items": [
            (1, 43, None),
            (44, 91, "1d4 minor"),
            (92, 100, "1 medium"),
        ],
    },
    10: {
        "coins": [
            (1, 10, None),
            (11, 24, "2d10 x 1,000 sp"),
            (25, 79, "6d4 x 100 gp"),
            (80, 100, "5d6 x 10 pp"),
        ],
        "goods": [
            (1, 35, None),
            (36, 79, "1d8 gems"),
            (80, 100, "1d6 art"),
        ],
        "items": [
            (1, 40, None),
            (41, 88, "1d4 minor"),
            (89, 99, "1 medium"),
            (100, 100, "1 major"),
        ],
    },
    11: {
        "coins": [
            (1, 8, None),
            (9, 14, "3d10 x 1,000 sp"),
            (15, 75, "4d8 x 100 gp"),
            (76, 100, "4d10 x 10 pp"),
        ],
        "goods": [
            (1, 24, None),
            (25, 74, "1d10 gems"),
            (75, 100, "1d6 art"),
        ],
        "items": [
            (1, 31, None),
            (32, 84, "1d4 minor"),
            (85, 98, "1 medium"),
            (99, 100, "1 major"),
        ],
    },
    12: {
        "coins": [
            (1, 8, None),
            (9, 14, "3d12 x 1,000 sp"),
            (15, 75, "1d4 x 1,000 gp"),
            (76, 100, "1d4 x 100 pp"),
        ],
        "goods": [
            (1, 17, None),
            (18, 70, "1d10 gems"),
            (71, 100, "1d8 art"),
        ],
        "items": [
            (1, 27, None),
            (28, 82, "1d6 minor"),
            (83, 97, "1 medium"),
            (98, 100, "1 major"),
        ],
    },
    13: {
        "coins": [
            (1, 8, None),
            (9, 75, "1d4 x 1,000 gp"),
            (76, 100, "1d10 x 100 pp"),
        ],
        "goods": [
            (1, 11, None),
            (12, 66, "1d12 gems"),
            (67, 100, "1d10 art"),
        ],
        "items": [
            (1, 19, None),
            (20, 73, "1d6 minor"),
            (74, 95, "1 medium"),
            (96, 100, "1 major"),
        ],
    },
    14: {
        "coins": [
            (1, 8, None),
            (9, 75, "1d6 x 1,000 gp"),
            (76, 100, "1d12 x 100 pp"),
        ],
        "goods": [
            (1, 11, None),
            (12, 66, "2d8 gems"),
            (67, 100, "2d6 art"),
        ],
        "items": [
            (1, 19, None),
            (20, 58, "1d6 minor"),
            (59, 92, "1 medium"),
            (93, 100, "1 major"),
        ],
    },
    15: {
        "coins": [
            (1, 3, None),
            (4, 74, "1d8 x 1,000 gp"),
            (75, 100, "3d4 x 100 pp"),
        ],
        "goods": [
            (1, 9, None),
            (10, 65, "2d10 gems"),
            (66, 100, "2d8 art"),
        ],
        "items": [
            (1, 11, None),
            (12, 46, "1d10 minor"),
            (47, 90, "1 medium"),
            (91, 100, "1 major"),
        ],
    },
    16: {
        "coins": [
            (1, 3, None),
            (4, 74, "1d12 x 1,000 gp"),
            (75, 100, "3d4 x 100 pp"),
        ],
        "goods": [
            (1, 7, None),
            (8, 64, "4d6 gems"),
            (65, 100, "2d10 art"),
        ],
        "items": [
            (1, 40, None),
            (41, 46, "1d10 minor"),
            (47, 90, "1d3 medium"),
            (91, 100, "1 major"),
        ],
    },
    17: {
        "coins": [
            (1, 3, None),
            (4, 68, "3d4 x 1,000 gp"),
            (69, 100, "2d10 x 100 pp"),
        ],
        "goods": [
            (1, 4, None),
            (5, 63, "4d8 gems"),
            (64, 100, "3d8 art"),
        ],
        "items": [
            (1, 33, None),
            (34, 83, "1d3 medium"),
            (84, 100, "1 major"),
        ],
    },
    18: {
        "coins": [
            (1, 2, None),
            (3, 65, "3d6 x 1,000 gp"),
            (66, 100, "5d4 x 100 pp"),
        ],
        "goods": [
            (1, 4, None),
            (5, 54, "3d12 gems"),
            (55, 100, "3d10 art"),
        ],
        "items": [
            (1, 24, None),
            (25, 80, "1d4 medium"),
            (81, 100, "1 major"),
        ],
    },
    19: {
        "coins": [
            (1, 2, None),
            (3, 65, "3d8 x 1,000 gp"),
            (66, 100, "3d10 x 100 pp"),
        ],
        "goods": [
            (1, 3, None),
            (4, 50, "6d6 gems"),
            (51, 100, "6d6 art"),
        ],
        "items": [
            (1, 4, None),
            (5, 70, "1d4 medium"),
            (71, 100, "1 major"),
        ],
    },
    20: {
        "coins": [
            (1, 2, None),
            (3, 65, "4d8 x 1,000 gp"),
            (66, 100, "4d10 x 100 pp"),
        ],
        "goods": [
            (1, 2, None),
            (3, 38, "4d10 gems"),
            (39, 100, "7d6 art"),
        ],
        "items": [
            (1, 25, None),
            (26, 65, "1d4 medium"),
            (66, 100, "1d3 major"),
        ],
    },
}

ADDITIONAL_MAJOR_ITEMS = {21: 1, 22: 2, 23: 4, 24: 6, 25: 9, 26: 12, 27: 17, 28: 23, 29: 31, 30: 42}

GEMS_TABLE = [
    (1, 25, "4d4", 10, ["ágata (banda, ojo o musgo)", "azurita", "cuarzo azul", "hematites", "lapislázuli", "malaquita", "obsidiana", "rodocrosita", "turquesa ojo de tigre", "perla de agua dulce"]),
    (26, 50, "2d4 x 10", 50, ["cornalina", "calcedonia", "crisoprasa", "citrino", "iolita", "jaspe", "piedra lunar", "ónice", "peridoto", "cristal de roca", "sardio", "sardónice", "cuarzo rosa", "cuarzo ahumado", "circón"]),
    (51, 70, "4d4 x 10", 100, ["ámbar", "amatista", "crisoberilo", "coral", "granate rojo o marrón verdoso", "jade", "azabache", "perla blanca, dorada, rosa o plateada", "espinela roja, rojo-marrón o verde oscuro", "turmalina"]),
    (71, 90, "2d4 x 100", 500, ["alejandrita", "aguamarina", "granate violeta", "perla negra", "espinela azul oscuro", "topacio amarillo dorado"]),
    (91, 99, "4d4 x 100", 1000, ["esmeralda", "ópalo blanco, negro o de fuego", "zafiro azul", "corindón púrpura intenso o amarillo vivo", "zafiro estrella azul o negro", "rubí estrella"]),
    (100, 100, "2d4 x 1,000", 5000, ["esmeralda verde brillante", "diamante azul-blanco, canario, rosa, marrón o azul", "jacinto"]),
]

ART_TABLE = [
    (1, 10, "1d10 x 10", 55, ["jarro de plata", "estatua tallada en hueso o marfil", "pulsera de oro pequeña finamente trabajada"]),
    (11, 25, "3d6 x 10", 105, ["vestimentas de tela de oro", "máscara de terciopelo negro con numerosos citrinos", "cáliz de plata con gemas de lapislázuli"]),
    (26, 40, "1d6 x 100", 350, ["tapiz de lana grande y bien hecho", "jarro de latón con incrustaciones de jade"]),
    (41, 50, "1d10 x 100", 550, ["peine de plata con piedras lunares", "espada larga de acero plateado con joya de azabache en la empuñadura"]),
    (51, 60, "2d6 x 100", 700, ["arpa tallada de madera exótica con incrustaciones de marfil y gemas de circón", "ídolo de oro macizo (4.5 kg)"]),
    (61, 70, "3d6 x 100", 1050, ["peine de dragón dorado con ojo de granate rojo", "tapón de botella de oro y topacio", "daga ceremonial de electro con rubí estrella en el pomo"]),
    (71, 80, "4d6 x 100", 1400, ["parche ocular con ojo falso de zafiro y piedra lunar", "colgante de ópalo de fuego en cadena de oro fino", "pintura antigua de un maestro"]),
    (81, 85, "5d6 x 100", 1750, ["manto de seda bordada y terciopelo con numerosas piedras lunares", "colgante de zafiro en cadena de oro"]),
    (86, 90, "1d4 x 1,000", 2500, ["guante bordado y enjoyado", "tobillera enjoyada", "caja de música de oro"]),
    (91, 95, "1d6 x 1,000", 3500, ["diadema de oro con cuatro aguamarinas", "collar de perlas rosas pequeñas"]),
    (96, 99, "2d4 x 1,000", 5000, ["corona de oro enjoyada", "anillo de electro enjoyado"]),
    (100, 100, "2d6 x 1,000", 7000, ["anillo de oro y rubí", "copa de oro con esmeraldas"]),
]

MUNDANE_TABLE: dict[str, Any] = {
    "categories": [
        (1, 17, "alquímico"),
        (18, 50, "armadura"),
        (51, 83, "arma"),
        (84, 100, "herramienta"),
    ],
    "alquímico": [
        (1, 12, "fuego de alquimista", "1d4 frascos", 20),
        (13, 24, "ácido", "2d4 frascos", 10),
        (25, 36, "barra de humo", "1d4 barras", 20),
        (37, 48, "agua bendita", "1d4 frascos", 25),
        (49, 62, "antitoxina", "1d4 dosis", 50),
        (63, 74, "antorcha eterna", "1", 0),
        (75, 88, "bolsas de brea", "1d4 bolsas", 50),
        (89, 100, "piedras de trueno", "1d4 piedras", 30),
    ],
}


def roll_dice(expression: str) -> int:
    expression = expression.replace(",", "").replace(" ", "").lower()
    match = re.match(r"(\d*)d(\d+)(?:\s*\*?\s*x?\s*(\d+))?", expression)
    if not match:
        return 0

    num = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    multiplier = int(match.group(3)) if match.group(3) else 1

    return sum(random.randint(1, sides) for _ in range(num)) * multiplier


def parse_dice_expression(expr: str) -> dict[str, Any]:
    if not expr:
        return {"result": 0, "detail": "nada"}

    # Parse "1d6 x 1,000 cp" → dice part + coin type
    match = re.match(r"(.+?)(?:\s+(cp|sp|gp|pp))?$", expr.strip())
    if not match:
        return {"result": 0, "detail": expr}

    dice_part = match.group(1).strip()
    coin_type = match.group(2)

    total = roll_dice(dice_part)

    result = {"result": total, "detail": expr, "coin_type": coin_type}

    if coin_type:
        result["coin_abbrev"] = COIN_ABBREV[coin_type]
        result["coin_name"] = COIN_NAMES[coin_type]
        result["total_gp"] = round(total * COIN_VALUE_IN_GP[coin_type], 2)

    return result


def resolve_tier(level: int) -> dict[str, list[tuple[int, str]]]:
    level = min(level, 30)

    if level <= 20:
        row = TREASURE_TABLE[level]
        return row

    row = TREASURE_TABLE[20]
    extra = ADDITIONAL_MAJOR_ITEMS.get(level, 0)
    if extra:
        items = row["items"].copy()
        # Express additional major items by expanding the last (major) range
        last = list(items[-1])
        if "major" in str(last[3]) if len(last) > 3 else False:
            last = (last[0], last[1], f"{last[2]} + {extra}")
            items[-1] = tuple(last)
        row = {**row, "items": items}
    return row


def roll_on_table(entries: list[tuple[int, int, Any]], bonus: int = 0) -> Any:
    roll = min(100, random.randint(1, 100) + bonus)
    for lo, hi, value in entries:
        if lo <= roll <= hi:
            return {"roll": roll - bonus, "value": value, "roll_modificado": roll}
    return {"roll": roll - bonus, "value": None, "roll_modificado": roll}


def resolve_goods_expression(expr: str) -> list[dict[str, Any]]:
    if not expr:
        return []

    if expr == "1 gem":
        return [random_gem()]
    if expr == "1 art":
        return [random_art_object()]

    match = re.match(r"(\d+)d(\d+)\s*(gems|art)$", expr)
    if match:
        num_dice = int(match.group(1))
        sides = int(match.group(2))
        count = sum(random.randint(1, sides) for _ in range(num_dice))
        if match.group(3) == "gems":
            return [random_gem() for _ in range(count)]
        else:
            return [random_art_object() for _ in range(count)]

    return []


def resolve_items_expression(expr: str, extra: int = 0) -> list[dict[str, Any]]:
    if not expr:
        return []

    match = re.match(r"(\d+)d(\d+)?\s*(mundane|minor|medium|major)$", expr)
    if match:
        num = int(match.group(1))
        if match.group(2):
            sides = int(match.group(2))
            count = sum(random.randint(1, sides) for _ in range(num))
        else:
            count = num
        count += extra
        tier = match.group(3)
        return [{"tier": tier} for _ in range(count)]

    match_single = re.match(r"1\s+(mundane|minor|medium|major)$", expr)
    if match_single:
        count = 1 + extra
        return [{"tier": match_single.group(1)} for _ in range(count)]

    return []


def random_gem() -> dict[str, Any]:
    gem_roll = random.randint(1, 100)
    for lo, hi, value_expr, avg, examples in GEMS_TABLE:
        if lo <= gem_roll <= hi:
            value = roll_dice(value_expr)
            name = random.choice(examples)
            return {"nombre": name, "valor": value, "promedio": avg, "tirada": gem_roll}
    return {"nombre": "gema", "valor": 0, "promedio": 0, "tirada": gem_roll}


def random_art_object() -> dict[str, Any]:
    art_roll = random.randint(1, 100)
    for lo, hi, value_expr, avg, examples in ART_TABLE:
        if lo <= art_roll <= hi:
            value = roll_dice(value_expr)
            name = random.choice(examples)
            return {"nombre": name, "valor": value, "promedio": avg, "tirada": art_roll}
    return {"nombre": "objeto de arte", "valor": 0, "promedio": 0, "tirada": art_roll}


def random_mundane_item() -> dict[str, Any]:
    cat_roll = random.randint(1, 100)
    category = "alquímico"
    for lo, hi, cat in MUNDANE_TABLE["categories"]:
        if lo <= cat_roll <= hi:
            category = cat
            break

    if category == "alquímico":
        sub_roll = random.randint(1, 100)
        for lo, hi, name, qty, cost in MUNDANE_TABLE["alquímico"]:
            if lo <= sub_roll <= hi:
                quantity = roll_dice(qty.split()[0]) if qty != "1" else 1
                total_cost = quantity * cost if cost else 0
                return {
                    "nombre": name,
                    "cantidad": quantity,
                    "coste_unitario": cost,
                    "coste_total": total_cost,
                    "categoria": "alquímico",
                }

    elif category == "armadura":
        size_roll = random.randint(1, 100)
        size = "Pequeña" if size_roll <= 10 else "Mediana"
        return {"nombre": f"Armadura ({size})", "categoria": "armadura"}

    elif category == "arma":
        weapon_roll = random.randint(1, 100)
        if weapon_roll <= 50:
            return {"nombre": "Arma cuerpo a cuerpo común maestra", "categoria": "arma"}
        elif weapon_roll <= 70:
            return {"nombre": "Arma poco común maestra", "categoria": "arma"}
        else:
            return {"nombre": "Arma a distancia común maestra", "categoria": "arma"}

    elif category == "herramienta":
        sub_roll = random.randint(1, 100)
        tools = [
            (1, 3, "Mochila vacía", 2),
            (4, 6, "Palanca", 2),
            (7, 11, "Linterna de ojo de buey", 12),
            (12, 16, "Candado simple", 20),
            (17, 21, "Candado normal", 40),
            (22, 28, "Candado bueno", 80),
            (29, 35, "Candado superior", 150),
            (36, 40, "Esposas maestras", 50),
            (41, 43, "Espejo pequeño de acero", 10),
            (44, 46, "Cuerda de seda (15 m)", 10),
            (47, 53, "Catalejo", 1000),
            (54, 58, "Herramientas de artesano maestras", 55),
            (59, 63, "Equipo de escalada", 80),
            (64, 68, "Kit de disfraz", 50),
            (69, 73, "Botiquín", 50),
            (74, 77, "Símbolo sagrado de plata", 25),
            (78, 81, "Reloj de arena", 25),
            (82, 88, "Lupa", 100),
            (89, 95, "Instrumento musical maestro", 100),
            (96, 100, "Herramientas de ladrón maestras", 50),
        ]
        for lo, hi, name, cost in tools:
            if lo <= sub_roll <= hi:
                return {"nombre": name, "coste": cost, "categoria": "herramienta"}

    return {"nombre": "Objeto mundano", "categoria": category}


def map_tier_to_rarity(tier: str, level: int) -> str:
    if tier not in RARITY_MAP:
        return "Raro"

    thresholds = sorted(RARITY_MAP[tier].keys())
    result = RARITY_MAP[tier][thresholds[0]]
    for t in thresholds:
        if level >= t:
            result = RARITY_MAP[tier][t]
    return result


def get_rarity_fallback_needed(count: int, rarity: str, available: int) -> tuple[str, int]:
    """If we need more items than available, return (fallback_rarity, remaining_count)."""
    if available >= count:
        return rarity, count
    idx = RARITY_FALLBACK.index(rarity)
    if idx + 1 < len(RARITY_FALLBACK):
        fallback = RARITY_FALLBACK[idx + 1]
        return fallback, count - available
    return rarity, available


class TreasureGenerator:
    def __init__(self, random_item_func=None):
        self._random_item_func = random_item_func

    def generate_full(self, level: int, tesoro_mayor: bool = False) -> dict[str, Any]:
        result = {"nivel": level, "tesoro_mayor": tesoro_mayor}
        bonus = 25 if tesoro_mayor else 0
        extra_items = 1 if tesoro_mayor else 0

        coins_result = self.roll_coins(level, bonus=bonus)
        result["monedas"] = coins_result

        goods_result = self.roll_goods(level, bonus=bonus)
        result["bienes"] = goods_result

        items_result = self.roll_items(level, bonus=bonus, extra=extra_items)
        result["items_srd"] = items_result

        magic_items = self._resolve_magic_items(items_result, level)
        result["objetos_magicos"] = magic_items

        total_gp = sum(c.get("total_gp", 0) for c in coins_result) + sum(b.get("valor", 0) for b in goods_result)
        for mi in magic_items:
            total_gp += mi.get("valor_estimado", 0)
        result["total_po_estimado"] = total_gp

        return result

    def roll_coins(self, level: int, bonus: int = 0) -> list[dict[str, Any]]:
        resolved = resolve_tier(level)
        entries = resolved["coins"]
        rolled = roll_on_table(entries, bonus=bonus)
        expr = rolled["value"]
        if not expr:
            return []

        parsed = parse_dice_expression(expr)
        return [parsed]

    def roll_goods(self, level: int, bonus: int = 0) -> list[dict[str, Any]]:
        resolved = resolve_tier(level)
        entries = resolved["goods"]
        rolled = roll_on_table(entries, bonus=bonus)
        return resolve_goods_expression(rolled["value"])

    def roll_items(self, level: int, bonus: int = 0, extra: int = 0) -> list[dict[str, Any]]:
        resolved = resolve_tier(level)
        entries = resolved["items"]
        rolled = roll_on_table(entries, bonus=bonus)
        return resolve_items_expression(rolled["value"], extra=extra)

    def _resolve_magic_items(self, items_srd: list[dict], level: int) -> list[dict[str, Any]]:
        result = []
        for item in items_srd:
            tier = item["tier"]
            if tier == "mundane":
                result.append({"tipo": "mundano", **random_mundane_item()})
            else:
                rarity = map_tier_to_rarity(tier, level)
                chosen = self._pick_random_item(rarity)
                if chosen:
                    result.append({**chosen, "rareza_origen": rarity, "tier_srd": tier})
                else:
                    result.append({"tipo": "objeto mágico", "tier_srd": tier, "rareza_origen": rarity, "nombre": f"[No disponible: {rarity}]"})
        return result

    def _pick_random_item(self, rarity: str):
        if not self._random_item_func:
            return None
        try:
            return self._random_item_func(rarity)
        except Exception:
            fallback_idx = RARITY_FALLBACK.index(rarity) + 1 if rarity in RARITY_FALLBACK else 1
            while fallback_idx < len(RARITY_FALLBACK):
                try:
                    return self._random_item_func(RARITY_FALLBACK[fallback_idx])
                except Exception:
                    fallback_idx += 1
            return None

    def expected_value(self, level: int) -> int:
        if level <= 20:
            return TREASURE_VALUES[level]
        return TREASURE_VALUES[20]
