"""MCP Dice Server - RPG dice rolling with full notation support.
Zero dependencies beyond Python 3 stdlib.
"""

import json
import random
import re
import sys


# ═══════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════

DAMAGE_TYPES = {
    "cortante": "cortante",
    "perforante": "perforante",
    "contundente": "contundente",
    "fuego": "fuego",
    "frio": "fr\u00edo",
    "rayo": "rayo",
    "acido": "\u00e1cido",
    "veneno": "veneno",
    "psiquico": "ps\u00edquico",
    "necrotico": "necr\u00f3tico",
    "radiante": "radiante",
    "fuerza": "fuerza",
}

DAMAGE_EMOJI = {
    "fuego": "\U0001f525",
    "frio": "\u2744\ufe0f",
    "rayo": "\u26a1",
    "acido": "\U0001f9ea",
    "veneno": "\U0001f922",
    "psiquico": "\U0001f9e0",
    "necrotico": "\U0001f480",
    "radiante": "\u2600\ufe0f",
    "fuerza": "\U0001f4aa",
}

COVER_BONUS = {"half": 2, "three_quarters": 5}
COVER_LABEL = {"half": "cobertura media", "three_quarters": "cobertura tres cuartos"}

DICE_CORE = re.compile(r"(\d+)d(\d+)(?:(kh|kl|dh|dl)(\d+))?")

FLAT_MOD_PATTERN = re.compile(r"[+-]\d+")


# ═══════════════════════════════════════════════
#  Dice Engine
# ═══════════════════════════════════════════════

def parse_notation(notation):
    """Parse a dice notation string into structured groups.

    Args:
        notation: e.g. "1d20+5", "2d20kh1+7", "1d8+2d6+3", "4d6kh3"

    Returns:
        {"groups": [...], "flat_modifier": int, "original": str}

    Rules:
      - For a single dice group, any +/-N after it is that group's modifier.
      - For multiple dice groups, any +/-N between or after groups goes to flat_modifier.
    """
    notation = notation.replace(" ", "")
    original = notation

    matches = list(DICE_CORE.finditer(notation))
    if not matches:
        return {"groups": [], "flat_modifier": 0, "original": original}

    groups = []
    for match in matches:
        count = int(match.group(1))
        sides = int(match.group(2))
        keep_drop = match.group(3)
        keep_drop_n = int(match.group(4)) if match.group(4) else None

        group = {"count": count, "sides": sides, "modifier": 0}

        if keep_drop == "kh":
            group["keep_highest"] = keep_drop_n
        elif keep_drop == "kl":
            group["keep_lowest"] = keep_drop_n
        elif keep_drop == "dh":
            group["drop_highest"] = keep_drop_n
        elif keep_drop == "dl":
            group["drop_lowest"] = keep_drop_n

        groups.append(group)

    # --- Determine modifiers ---
    if len(groups) == 1:
        # Single group: any modifier after the dice is the group's modifier
        tail = notation[matches[0].end():]
        m = re.match(r"^([+-]\d+)$", tail)
        if m:
            groups[0]["modifier"] = int(m.group(1))
        flat_modifier = 0
    else:
        # Multiple groups: extract flat modifier from non-dice segments
        non_dice = notation
        for match in matches:
            non_dice = non_dice.replace(match.group(0), "|", 1)
        parts = non_dice.split("|")
        flat_modifier = 0
        for part in parts:
            for mod_str in FLAT_MOD_PATTERN.findall(part):
                flat_modifier += int(mod_str)

    return {"groups": groups, "flat_modifier": flat_modifier, "original": original}


def roll_notation(notation, rng=None):
    """Roll a dice notation string.

    Args:
        notation: e.g. "1d20+5"
        rng: callable(int, int) -> int, defaults to random.randint

    Returns dict with full roll details.
    """
    if rng is None:
        rng = random.randint

    parsed = parse_notation(notation)

    if not parsed["groups"]:
        raise ValueError(f"Invalid dice notation: {notation!r}")

    groups_results = []

    for group in parsed["groups"]:
        count = group["count"]
        sides = group["sides"]
        modifier = group.get("modifier", 0)

        rolls = [rng(1, sides) for _ in range(count)]
        kept = list(rolls)
        dropped = []

        if "keep_highest" in group:
            n = group["keep_highest"]
            sorted_r = sorted(rolls, reverse=True)
            kept = sorted_r[:n]
            dropped = sorted_r[n:]
        elif "keep_lowest" in group:
            n = group["keep_lowest"]
            sorted_r = sorted(rolls)
            kept = sorted_r[:n]
            dropped = sorted_r[n:]
        elif "drop_highest" in group:
            n = group["drop_highest"]
            sorted_r = sorted(rolls, reverse=True)
            kept = sorted_r[n:]
            dropped = sorted_r[:n]
        elif "drop_lowest" in group:
            n = group["drop_lowest"]
            sorted_r = sorted(rolls)
            kept = sorted_r[n:]
            dropped = sorted_r[:n]

        group_total = sum(kept) + modifier

        gr = {
            "count": count,
            "sides": sides,
            "modifier": modifier,
            "rolls": rolls,
            "kept": kept,
            "dropped": dropped,
            "total": group_total,
        }
        for k in ("keep_highest", "keep_lowest", "drop_highest", "drop_lowest"):
            if k in group:
                gr[k] = group[k]

        if sides == 20:  # d20 crit/fumble on final kept values
            gr["is_crit"] = 20 in kept
            gr["is_fumble"] = 1 in kept

        groups_results.append(gr)

    total = sum(g["total"] for g in groups_results) + parsed["flat_modifier"]

    d20_group = next((g for g in groups_results if g["sides"] == 20), None)
    is_crit = d20_group.get("is_crit", False) if d20_group else False
    is_fumble = d20_group.get("is_fumble", False) if d20_group else False

    return {
        "notation": notation,
        "parsed": parsed,
        "groups": groups_results,
        "flat_modifier": parsed["flat_modifier"],
        "total": total,
        "is_crit": is_crit,
        "is_fumble": is_fumble,
    }


# ═══════════════════════════════════════════════
#  Display Formatter
# ═══════════════════════════════════════════════

def format_group_display(g):
    """Format a single group result for display.

    e.g. '1d20(13)', '2d20(7,15) \u2192 15', '4d6(6,3,1,4) \u2192 (6,4,3)'
    """
    roll_str = f"{g['count']}d{g['sides']}({','.join(str(r) for r in g['rolls'])})"

    has_keep_drop = any(
        g.get(k) is not None
        for k in ("keep_highest", "keep_lowest", "drop_highest", "drop_lowest")
    )

    if has_keep_drop:
        kept_sorted = sorted(g["kept"], reverse=True)
        kept_str = ",".join(str(r) for r in kept_sorted)
        if g.get("modifier"):
            return f"{roll_str} \u2192 {kept_str}"
        else:
            return f"{roll_str} \u2192 ({kept_str})"
    else:
        return roll_str


def format_roll_display(result):
    """Format the full roll result as a display string.

    e.g. '1d20(13) + 5 = 18', '2d20(7,15) \u2192 15 + 7 = 22'
    """
    parts = []
    for g in result["groups"]:
        group_str = format_group_display(g)
        mod = g.get("modifier", 0)
        if mod:
            sign = "+" if mod > 0 else "-"
            group_str += f" {sign} {abs(mod)}"
        parts.append(group_str)

    display = " + ".join(parts)

    flat = result.get("flat_modifier", 0)
    if flat:
        sign = "+" if flat > 0 else "-"
        display += f" {sign} {abs(flat)}"

    display += f" = {result['total']}"

    return display


def get_target_emoji(is_crit, is_fumble, success):
    """Get the result emoji for a check vs target."""
    if is_crit:
        return "\U0001f525 CR\u00cdTICO"
    if is_fumble:
        return "PIFIA"
    if success:
        return "\u2705 ACIERTO"
    return "\u274c FALLO"


def get_save_emoji(is_crit, is_fumble, success):
    """Get the result emoji for a saving throw."""
    if is_crit:
        return "\U0001f525 CR\u00cdTICO"
    if is_fumble:
        return "PIFIA"
    if success:
        return "\u2705 SALVADA"
    return "\u274c FALLIDA"


def get_check_emoji(is_crit, is_fumble, success):
    """Get the result emoji for an ability check."""
    if is_crit:
        return "\U0001f525 CR\u00cdTICO"
    if is_fumble:
        return "PIFIA"
    if success:
        return "\u2705 \u00c9XITO"
    return "\u274c FALLO"


def get_death_save_emoji(success):
    return "\u2705 \u00c9XITO" if success else "\u274c FALLO"


def format_target_comparison(result, target, target_type):
    """Format the comparison against AC/DC."""
    label = "CA" if target_type == "ac" else "CD"
    op = "\u2265" if result["total"] >= target else "<"
    return f"{op} {label} {target}"


# ═══════════════════════════════════════════════
#  Action Output Formatters
# ═══════════════════════════════════════════════

def detect_advantage_text(result):
    """Detect VENTAJA/DESVENTAJA from keep patterns on d20."""
    for g in result["groups"]:
        if g["sides"] == 20:
            if g.get("keep_highest") == 1:
                return "VENTAJA"
            if g.get("keep_lowest") == 1:
                return "DESVENTAJA"
    return None


def fmt_attack(params, main_result, damage_result):
    """Format an attack action output."""
    content = []
    label = params["label"]
    target = params.get("target")
    target_type = params.get("target_type", "ac")
    damage_type = params.get("damage_type")
    tags = params.get("tags", [])
    cover = params.get("cover")
    resistance = params.get("resistance")

    display = format_roll_display(main_result)

    adv_text = detect_advantage_text(main_result)

    tag_prefix = ""
    if "opportunity" in tags:
        tag_prefix = "\u26a1 OPORTUNIDAD: "
    if adv_text:
        tag_prefix = f"{adv_text} {tag_prefix}"

    line1 = f"[{label}] {tag_prefix}{display}"

    label_t = "CA" if target_type == "ac" else "CD"

    effective_target = target
    hit = None

    if target is not None:
        cover_text = ""
        if cover and target_type == "ac":
            bonus = COVER_BONUS.get(cover, 0)
            effective_target = target + bonus
            cover_text = f" + {bonus} ({COVER_LABEL.get(cover, cover)})"

        target_display = f"{label_t} {target}{cover_text}"
        if cover:
            target_display += f" = {effective_target}"

        hit = main_result["total"] >= effective_target

        if main_result["is_crit"]:
            line1 += f" \u2265 {target_display} \u2192 \U0001f525 CR\u00cdTICO"
        elif main_result["is_fumble"]:
            line1 += " \u2192 PIFIA"
        else:
            op = "\u2265" if hit else "<"
            line1 += f" {op} {target_display} \u2192 {'\u2705 ACIERTO' if hit else '\u274c FALLO'}"
    else:
        if main_result["is_crit"]:
            line1 += " \u2192 \U0001f525 CR\u00cdTICO"
        elif main_result["is_fumble"]:
            line1 += " \u2192 PIFIA"

    content.append({"type": "text", "text": line1})

    show_damage = damage_result and (target is None or hit or main_result["is_crit"])
    if show_damage:
        dmg_display = format_roll_display(damage_result)
        dmg_emoji = DAMAGE_EMOJI.get(damage_type, "\U0001fa78")
        dmg_type_name = DAMAGE_TYPES.get(damage_type, damage_type or "")
        dmg_text = f"  Da\u00f1o: {dmg_display} {dmg_type_name} {dmg_emoji}"

        if resistance and damage_type and resistance.lower() == damage_type.lower():
            dmg_half = damage_result["total"] // 2
            dmg_text += f" \u2192 RESISTENCIA \U0001f6e1\ufe0f \u2192 {dmg_half} {dmg_type_name} {dmg_emoji}"

        content.append({"type": "text", "text": dmg_text})

    return content


def fmt_save(params, main_result, damage_result):
    """Format a saving throw action output."""
    content = []
    label = params["label"]
    target = params.get("target")
    target_type = params.get("target_type", "dc")
    half_on_save = params.get("half_on_save", False)
    condition = params.get("condition")
    damage_type = params.get("damage_type")
    resistance = params.get("resistance")
    immunity = params.get("immunity")

    display = format_roll_display(main_result)
    label_t = "CD" if target_type == "dc" else "CA"

    line1 = f"[{label}] {display}"

    if target is not None:
        success = main_result["total"] >= target
        op = "\u2265" if success else "<"
        emoji = "\u2705 SALVADA" if success else "\u274c FALLIDA"
        line1 += f" {op} {label_t} {target} \u2192 {emoji}"
    else:
        line1 += f" = {main_result['total']}"

    content.append({"type": "text", "text": line1})

    if damage_result:
        dmg_display = format_roll_display(damage_result)
        dmg_emoji = DAMAGE_EMOJI.get(damage_type, "\U0001fa78")
        dmg_type_name = DAMAGE_TYPES.get(damage_type, damage_type or "")

        if immunity and damage_type and immunity.lower() == damage_type.lower():
            content.append({"type": "text", "text": f"  Criatura: inmune al {dmg_type_name} \U0001f6e1\ufe0f \u2192 0 da\u00f1o"})
        elif success and half_on_save:
            dmg_half = damage_result["total"] // 2
            content.append({"type": "text", "text": f"  Da\u00f1o: {dmg_display} / 2 = {dmg_half} {dmg_type_name} {dmg_emoji}"})
        else:
            dmg_text = f"  Da\u00f1o: {dmg_display} {dmg_type_name} {dmg_emoji}"
            if resistance and damage_type and resistance.lower() == damage_type.lower():
                dmg_half = damage_result["total"] // 2
                dmg_text += f" \u2192 RESISTENCIA \U0001f6e1\ufe0f \u2192 {dmg_half} {dmg_type_name} {dmg_emoji}"
            content.append({"type": "text", "text": dmg_text})

    if condition and not (target and main_result["total"] >= target):
        content.append({"type": "text", "text": f"  Estado: {condition} \u2620\ufe0f"})

    return content


def fmt_check(params, main_result, _damage_result):
    """Format an ability check action output."""
    label = params["label"]
    target = params.get("target")
    target_type = params.get("target_type", "dc")

    display = format_roll_display(main_result)
    label_t = "CD" if target_type == "dc" else "CA"

    line1 = f"[{label}] {display}"

    if target is not None:
        success = main_result["total"] >= target
        op = "\u2265" if success else "<"
        emoji = "\u2705 \u00c9XITO" if success else "\u274c FALLO"
        line1 += f" {op} {label_t} {target} \u2192 {emoji}"
    else:
        line1 += f" = {main_result['total']}"

    return [{"type": "text", "text": line1}]


def fmt_heal(params, main_result, _damage_result):
    """Format a healing action output."""
    label = params["label"]
    current_hp = params.get("current_hp", 0)
    max_hp = params.get("max_hp", 0)

    display = format_roll_display(main_result)
    heal_amount = main_result["total"]
    new_hp = min(current_hp + heal_amount, max_hp) if max_hp else current_hp + heal_amount

    content = [
        {"type": "text", "text": f"[{label}] \U0001f49a Recuperas {display} PG"},
    ]
    if max_hp:
        content.append({"type": "text", "text": f"  PG: {new_hp}/{max_hp}"})
    else:
        content.append({"type": "text", "text": f"  PG: {new_hp}"})

    return content


def fmt_damage(params, main_result, _damage_result):
    """Format a direct damage action output."""
    label = params["label"]
    damage_type = params.get("damage_type")
    resistance = params.get("resistance")
    immunity = params.get("immunity")

    display = format_roll_display(main_result)
    dmg_emoji = DAMAGE_EMOJI.get(damage_type, "\U0001fa78")
    dmg_type_name = DAMAGE_TYPES.get(damage_type, damage_type or "")

    if immunity and damage_type and immunity.lower() == damage_type.lower():
        return [
            {"type": "text", "text": f"[{label}] {display} {dmg_type_name} {dmg_emoji}"},
            {"type": "text", "text": f"  Criatura: inmune al {dmg_type_name} \U0001f6e1\ufe0f \u2192 0 da\u00f1o"},
        ]

    text = f"[{label}] {display} {dmg_type_name} {dmg_emoji}"
    if resistance and damage_type and resistance.lower() == damage_type.lower():
        dmg_half = main_result["total"] // 2
        text += f" \u2192 RESISTENCIA \U0001f6e1\ufe0f \u2192 {dmg_half} {dmg_type_name} {dmg_emoji}"

    return [{"type": "text", "text": text}]


def fmt_death_save(params, main_result, _damage_result):
    """Format a death saving throw output."""
    label = params["label"]
    successes = params.get("successes", 0)
    fails = params.get("fails", 0)

    display = format_roll_display(main_result)
    roll_value = main_result["total"]

    if roll_value >= 10:
        successes += 1
        emoji = "\u2705 \u00c9XITO"
    else:
        fails += 1
        emoji = "\u274c FALLO"

    line1 = f"[{label}] {display} \u2265 10 \u2192 {emoji} ({successes}/3 \u00e9xitos, {fails}/3 fallos)"
    return [{"type": "text", "text": line1}]


def fmt_spell(params, main_result, damage_result):
    """Format a spell action output."""
    label = params["label"]
    target = params.get("target")
    target_type = params.get("target_type", "ac")
    damage_type = params.get("damage_type")
    half_on_save = params.get("half_on_save", False)
    condition = params.get("condition")
    immunity = params.get("immunity")

    display = format_roll_display(main_result)
    dmg_emoji = DAMAGE_EMOJI.get(damage_type, "\u2728")
    dmg_type_name = DAMAGE_TYPES.get(damage_type, damage_type or "")

    content = []

    if target is not None:
        label_t = "CA" if target_type == "ac" else "CD"
        success = main_result["total"] >= target
        op = "\u2265" if success else "<"
        if target_type == "ac":
            emoji = get_target_emoji(main_result["is_crit"], main_result["is_fumble"], success)
        else:
            emoji = "\u2705 SALVADA" if success else "\u274c FALLIDA"
        line1 = f"[{label}] \u2728 {display} {op} {label_t} {target} \u2192 {emoji}"
    else:
        line1 = f"[{label}] \u2728 {display} = {main_result['total']}"
        success = True

    content.append({"type": "text", "text": line1})

    show_spell_dmg = (
        damage_result
        and (target_type != "ac" or success or main_result["is_crit"])
    )

    if show_spell_dmg:
        dmg_display = format_roll_display(damage_result)

        if immunity and damage_type and immunity.lower() == damage_type.lower():
            content.append({"type": "text", "text": f"  Criatura: inmune al {dmg_type_name} \U0001f6e1\ufe0f \u2192 0 da\u00f1o"})
        elif success and half_on_save and target:
            dmg_half = damage_result["total"] // 2
            content.append({"type": "text", "text": f"  Da\u00f1o: {dmg_display} / 2 = {dmg_half} {dmg_type_name} {dmg_emoji}"})
        else:
            content.append({"type": "text", "text": f"  Da\u00f1o: {dmg_display} {dmg_type_name} {dmg_emoji}"})

    if condition and not (target and main_result["total"] >= target):
        content.append({"type": "text", "text": f"  Estado: {condition} \u2620\ufe0f"})

    return content


def fmt_custom(params, main_result, _damage_result):
    """Format a custom roll action output."""
    label = params["label"]
    display = format_roll_display(main_result)
    return [{"type": "text", "text": f"[{label}] {display}"}]


ACTION_FORMATTERS = {
    "attack": fmt_attack,
    "save": fmt_save,
    "check": fmt_check,
    "heal": fmt_heal,
    "damage": fmt_damage,
    "death_save": fmt_death_save,
    "spell": fmt_spell,
    "custom": fmt_custom,
}


# ═══════════════════════════════════════════════
#  Tool Registry & Execution
# ═══════════════════════════════════════════════

TOOLS = [
    {
        "name": "roll",
        "title": "Tirar dados RPG",
        "description": "Realiza tiradas de dados RPG (D&D 5e y similares). Soporta 8 tipos de acci\u00f3n: attack, save, check, heal, damage, death_save, spell, custom.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["attack", "save", "check", "heal", "damage", "death_save", "spell", "custom"],
                    "description": (
                        "Tipo de acci\u00f3n RPG. Elegir seg\u00fan el contexto:\n"
                        '- "attack": ataque con arma (tirada vs CA). Usar con target, target_type="ac", damage_notation, damage_type. Muestra da\u00f1o si acierta.\n'
                        '- "save": tirada de salvaci\u00f3n (vs CD). Si half_on_save=true, el da\u00f1o se reduce a la mitad al superar la CD. Usar condition si fallar aplica un estado.\n'
                        '- "check": prueba de habilidad (Atletismo, Sigilo, etc.). Solo tirada vs CD, sin da\u00f1o.\n'
                        '- "heal": tirada de curaci\u00f3n. Requiere current_hp y max_hp. La curaci\u00f3n se limita autom\u00e1ticamente a max_hp.\n'
                        '- "damage": solo tirada de da\u00f1o directo, sin ataque previo. Usar con resistance/immunity si aplica.\n'
                        '- "death_save": salvaci\u00f3n contra muerte (CD 10). Pasar successes y fails acumulados. Si notation se omite, usa 1d20 por defecto.\n'
                        '- "spell": conjuro. Con target_type="ac" es ataque m\u00e1gico; con target_type="dc" es salvaci\u00f3n. half_on_save solo aplica a saves.\n'
                        '- "custom": tirada libre sin formato RPG. Solo muestra el resultado crudo de los dados.'
                    ),
                },
                "label": {
                    "type": "string",
                    "description": "Nombre descriptivo: arma (ESPADA LARGA), conjuro (BOLA DE FUEGO), habilidad (ATLETISMO), salvaci\u00f3n (SALV. DESTREZA), etc.",
                },
                "notation": {
                    "type": "string",
                    "description": (
                        "Notaci\u00f3n de dados. Formatos soportados:\n"
                        "- 1d20+5, 2d6, 8d6 (tiradas b\u00e1sicas con/sin modificador)\n"
                        "- 2d20kh1+7 (VENTAJA: tira 2d20, keep highest 1, suma +7)\n"
                        "- 2d20kl1+2 (DESVENTAJA: tira 2d20, keep lowest 1, suma +2)\n"
                        "- 4d6kh3 (tira 4d6, keep highest 3 \u2014 para stats D&D)\n"
                        "- 5d6dh2, 5d6dl2 (drop highest/lowest N dados)\n"
                        "- 1d8+2d6+3 (m\u00faltiples grupos de dados + modificador plano al final)"
                    ),
                },
                "target": {
                    "type": "number",
                    "description": "CA (Clase de Armadura) o CD (Dificultad de Clase) a superar con la tirada",
                },
                "target_type": {
                    "type": "string",
                    "enum": ["ac", "dc"],
                    "description": '"ac" para tiradas de ataque (Clase de Armadura), "dc" para salvaciones y pruebas de habilidad (Dificultad de Clase). Default: "ac"',
                },
                "damage_notation": {
                    "type": "string",
                    "description": "Notaci\u00f3n de dados de da\u00f1o, separada de la tirada de ataque. Ej: 1d8+3, 2d6, 8d6. Solo se aplica si el ataque acierta.",
                },
                "damage_type": {
                    "type": "string",
                    "enum": list(DAMAGE_TYPES.keys()),
                    "description": "Tipo de da\u00f1o: cortante, perforante, contundente, fuego, fr\u00edo, rayo, \u00e1cido, veneno, ps\u00edquico, necr\u00f3tico, radiante, fuerza",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": 'Etiquetas opcionales. Valores: "opportunity" (ataque de oportunidad \u26a1)',
                },
                "resistance": {
                    "type": "string",
                    "description": "Tipo de da\u00f1o al que la criatura es resistente (reduce da\u00f1o a la mitad). Debe coincidir con damage_type.",
                },
                "immunity": {
                    "type": "string",
                    "description": "Tipo de da\u00f1o al que la criatura es inmune (0 da\u00f1o). Debe coincidir con damage_type.",
                },
                "cover": {
                    "type": "string",
                    "enum": ["half", "three_quarters"],
                    "description": "Cobertura del objetivo: half (+2 CA), three_quarters (+5 CA). Solo aplica con target_type=\"ac\".",
                },
                "half_on_save": {
                    "type": "boolean",
                    "description": "Si es true, el da\u00f1o se reduce a la mitad cuando la salvaci\u00f3n tiene \u00e9xito. Usar con action=\"save\" o action=\"spell\"+target_type=\"dc\".",
                },
                "condition": {
                    "type": "string",
                    "description": "Condici\u00f3n aplicada si la salvaci\u00f3n falla (ej: envenenado, asustado, paralizado). Se muestra en el output con \u2620\ufe0f.",
                },
                "current_hp": {
                    "type": "number",
                    "description": "PG actuales del personaje antes de la curaci\u00f3n. Usar solo con action=\"heal\".",
                },
                "max_hp": {
                    "type": "number",
                    "description": "PG m\u00e1ximos del personaje. La curaci\u00f3n no puede superar este valor. Usar solo con action=\"heal\".",
                },
                "successes": {
                    "type": "number",
                    "description": "Salvaciones de muerte exitosas acumuladas (0-2). Se incrementa autom\u00e1ticamente si la tirada >= 10. Usar con action=\"death_save\".",
                },
                "fails": {
                    "type": "number",
                    "description": "Fallos de salvaci\u00f3n de muerte acumulados (0-2). Se incrementa autom\u00e1ticamente si la tirada < 10. Usar con action=\"death_save\".",
                },
            },
            "required": ["action", "label", "notation"],
        },
    },
    {
        "name": "roll_stats",
        "title": "Generar estad\u00edsticas",
        "description": "Genera 6 valores de estad\u00edsticas estilo D&D 5e.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["standard", "heroic"],
                    "description": "M\u00e9todo: standard (4d6kh3) o heroic (2d6+6)",
                },
            },
        },
    },
]


def validate_roll_params(params):
    """Validate and normalize roll tool parameters."""
    action = params.get("action")
    if action not in ACTION_FORMATTERS:
        raise ValueError(f"Invalid action: {action!r}. Must be one of {list(ACTION_FORMATTERS.keys())}")

    notation = params.get("notation", "")
    if not notation and action != "death_save":
        raise ValueError("Missing required parameter: notation")

    if notation:
        parsed = parse_notation(notation)
        if not parsed["groups"]:
            raise ValueError(f"Invalid dice notation: {notation!r}")

    return params


def execute_roll(params):
    """Execute the roll tool and return MCP content."""
    params = validate_roll_params(params)
    action = params["action"]

    notation = params.get("notation", "")
    damage_notation = params.get("damage_notation", "")

    # Handle death_save default notation
    if not notation and action == "death_save":
        notation = "1d20"

    main_result = roll_notation(notation) if notation else None
    damage_result = roll_notation(damage_notation) if damage_notation else None

    formatter = ACTION_FORMATTERS[action]
    content = formatter(params, main_result, damage_result)

    return {"content": content}


def execute_roll_stats(params):
    """Execute the roll_stats tool."""
    method = params.get("method", "standard")

    if method == "heroic":
        notation = "2d6+6"
    else:
        notation = "4d6kh3"

    stats = []
    for _ in range(6):
        result = roll_notation(notation)
        stats.append({
            "roll_display": format_roll_display(result),
            "total": result["total"],
        })

    lines = ["[Estad\u00edsticas RPG]"]
    for i, s in enumerate(stats, 1):
        lines.append(f"  Stat {i}: {s['roll_display']}")

    total_sum = sum(s["total"] for s in stats)
    lines.append(f"  Suma total: {total_sum}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


TOOL_HANDLERS = {
    "roll": execute_roll,
    "roll_stats": execute_roll_stats,
}


# ═══════════════════════════════════════════════
#  MCP Protocol Handlers
# ═══════════════════════════════════════════════

def handle_initialize(_params, req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "dice-mcp", "version": "1.0.0"},
        },
    }


def handle_tools_list(_params, req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {"tools": TOOLS},
    }


def handle_tools_call(params, req_id):
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
        }

    try:
        result = handler(arguments)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    except ValueError as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32602, "message": str(e)},
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32603, "message": f"Internal error: {e}"},
        }


METHOD_HANDLERS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


def process_message(message):
    """Process a single JSON-RPC message."""
    method = message.get("method")
    params = message.get("params", {})
    req_id = message.get("id")

    # Notifications have no id
    if req_id is None:
        if method == "notifications/initialized":
            return None
        # Silently ignore other notifications
        return None

    handler = METHOD_HANDLERS.get(method)
    if handler:
        return handler(params, req_id)

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def run_server():
    """Run the MCP server main loop."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = process_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_server()
