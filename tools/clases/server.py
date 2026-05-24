"""MCP server for D&D 2024 Spanish PHB data (classes, subclasses, features, spells)."""
import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("D&D2024_ES")

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def _load(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

CLASSES = {c['id']: c for c in _load('classes.json')}
SUBCLASSES = {s['id']: s for s in _load('subclasses.json')}
FEATURES = _load('features.json')
SPELLS = {s['id']: s for s in _load('spells.json')}

# ---------- RESOURCES ----------

@mcp.resource("classes://all")
def get_all_classes() -> str:
    """Return all classes as JSON."""
    return json.dumps(list(CLASSES.values()), ensure_ascii=False, indent=2)

@mcp.resource("classes://{class_id}")
def get_class(class_id: str) -> str:
    """Return a single class by ID."""
    c = CLASSES.get(class_id)
    if not c:
        return json.dumps({"error": f"Class '{class_id}' not found"}, ensure_ascii=False)
    return json.dumps(c, ensure_ascii=False, indent=2)

@mcp.resource("subclasses://all")
def get_all_subclasses() -> str:
    """Return all subclasses as JSON."""
    return json.dumps(list(SUBCLASSES.values()), ensure_ascii=False, indent=2)

@mcp.resource("subclasses://{subclass_id}")
def get_subclass(subclass_id: str) -> str:
    """Return a single subclass by ID."""
    s = SUBCLASSES.get(subclass_id)
    if not s:
        return json.dumps({"error": f"Subclass '{subclass_id}' not found"}, ensure_ascii=False)
    return json.dumps(s, ensure_ascii=False, indent=2)

@mcp.resource("features://all")
def get_all_features() -> str:
    """Return all features as JSON."""
    return json.dumps(FEATURES, ensure_ascii=False, indent=2)

@mcp.resource("spells://all")
def get_all_spells() -> str:
    """Return all spells as JSON."""
    return json.dumps(list(SPELLS.values()), ensure_ascii=False, indent=2)

@mcp.resource("spells://{spell_id}")
def get_spell(spell_id: str) -> str:
    """Return a single spell by ID."""
    s = SPELLS.get(spell_id)
    if not s:
        return json.dumps({"error": f"Spell '{spell_id}' not found"}, ensure_ascii=False)
    return json.dumps(s, ensure_ascii=False, indent=2)

# ---------- TOOLS ----------

@mcp.tool()
def get_class_info(class_id: str) -> str:
    """Get summary info for a class (ID in Spanish, e.g. 'bárbaro', 'mago')."""
    c = CLASSES.get(class_id)
    if not c:
        return json.dumps({"error": f"Class '{class_id}' not found"}, ensure_ascii=False)
    return json.dumps({
        "name": c["name"],
        "primary_ability": c["primary_ability"],
        "hit_die": c["hit_die"],
        "saving_throws": c["saving_throws"],
        "skill_count": c["skill_count"],
        "skill_options": c["skill_options"],
        "weapons": c["weapons"],
        "armor": c["armor"],
        "tools": c["tools"],
        "spellcasting_ability": c["spellcasting_ability"],
        "spellcasting_type": c["spellcasting_type"],
        "subclasses": [SUBCLASSES[sid]["name"] for sid in c["subclasses"]],
    }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_class_features(class_id: str) -> str:
    """Get all class features (not subclass) for a class."""
    feats = [f for f in FEATURES if f.get('class_id') == class_id and f.get('subclass_id') is None]
    feats.sort(key=lambda x: (x['level'], x['name']))
    return json.dumps(feats, ensure_ascii=False, indent=2)

@mcp.tool()
def get_subclass_features(subclass_id: str) -> str:
    """Get all features for a specific subclass."""
    feats = [f for f in FEATURES if f.get('subclass_id') == subclass_id]
    feats.sort(key=lambda x: (x['level'], x['name']))
    return json.dumps(feats, ensure_ascii=False, indent=2)

@mcp.tool()
def get_subclasses_for_class(class_id: str) -> str:
    """Get all subclasses for a class."""
    c = CLASSES.get(class_id)
    if not c:
        return json.dumps({"error": f"Class '{class_id}' not found"}, ensure_ascii=False)
    subs = [SUBCLASSES[sid] for sid in c["subclasses"] if sid in SUBCLASSES]
    return json.dumps(subs, ensure_ascii=False, indent=2)

@mcp.tool()
def get_spell_list(class_id: str, level: int = -1) -> str:
    """Get spells available to a class. level=-1 means all levels."""
    spells = [s for s in SPELLS.values() if class_id in s.get('classes', [])]
    if level >= 0:
        spells = [s for s in spells if s['level'] == level]
    spells.sort(key=lambda x: (x['level'], x['name']))
    return json.dumps(spells, ensure_ascii=False, indent=2)

@mcp.tool()
def search_spells(query: str = "", school: str = "", level: int = -1, class_id: str = "") -> str:
    """Search spells by name substring, school, level, or class. Empty/negative means any."""
    results = list(SPELLS.values())
    if query:
        q = query.lower()
        results = [s for s in results if q in s['name'].lower()]
    if school:
        results = [s for s in results if s['school'].lower() == school.lower()]
    if level >= 0:
        results = [s for s in results if s['level'] == level]
    if class_id:
        results = [s for s in results if class_id in s.get('classes', [])]
    results.sort(key=lambda x: (x['level'], x['name']))
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool()
def search_features(query: str = "", level: int = -1, class_id: str = "", subclass_id: str = "") -> str:
    """Search features by name substring, level, class, or subclass. Empty/negative means any."""
    results = list(FEATURES)
    if query:
        q = query.lower()
        results = [f for f in results if q in f['name'].lower()]
    if level >= 0:
        results = [f for f in results if f['level'] == level]
    if class_id:
        results = [f for f in results if f.get('class_id') == class_id]
    if subclass_id:
        results = [f for f in results if f.get('subclass_id') == subclass_id]
    results.sort(key=lambda x: (x['level'], x['name']))
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool()
def get_feature_by_id(feature_id: str) -> str:
    """Get a single feature by its ID."""
    feat = next((f for f in FEATURES if f.get('id') == feature_id), None)
    if not feat:
        return json.dumps({"error": f"Feature '{feature_id}' not found"}, ensure_ascii=False)
    return json.dumps(feat, ensure_ascii=False, indent=2)

@mcp.tool()
def list_classes() -> str:
    """List all class IDs and names."""
    return json.dumps([{"id": c["id"], "name": c["name"]} for c in CLASSES.values()], ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()
