"""
Monster database: search, filter, and retrieve monster data.
"""
from src.monster_schema import normalize_name, normalize_text


class MonsterDB:
    """In-memory monster database with search and filter capabilities."""

    def __init__(self, monsters: list[dict]):
        self._monsters = monsters
        self._build_index()

    def _build_index(self):
        """Build normalized name index for fast lookup."""
        self._name_index = {}
        for m in self._monsters:
            norm = normalize_name(m["name"])
            if norm not in self._name_index:
                self._name_index[norm] = []
            self._name_index[norm].append(m)

        # Build sorted lists of unique values
        self._types = sorted(set(m["type"] for m in self._monsters if m["type"]))
        self._sizes = sorted(set(m["size"] for m in self._monsters if m["size"]))
        self._alignments = sorted(set(m["alignment"] for m in self._monsters if m["alignment"]))
        self._crs = sorted(set(m["cr"] for m in self._monsters if m["cr"]), key=self._cr_sort_key)

        habitats = set()
        for m in self._monsters:
            for h in m.get("habitat", []):
                if h:
                    habitats.add(h)
        self._habitats = sorted(habitats)

    @staticmethod
    def _cr_sort_key(cr: str) -> float:
        from src.monster_schema import cr_to_numeric
        return cr_to_numeric(cr)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Search monsters by name (partial, accent-insensitive, case-insensitive).

        Returns list of monsters with basic fields (name, type, cr, size, alignment).
        """
        if not query or not query.strip():
            return []

        query_norm = normalize_name(query)
        matches = []

        for m in self._monsters:
            name_norm = normalize_name(m["name"])
            if query_norm in name_norm:
                matches.append(self._summary(m))

        return matches[:limit]

    def get_monster(self, name: str) -> dict | None:
        """Get full monster data by name (case/accent insensitive exact match)."""
        if not name:
            return None

        name_norm = normalize_name(name)

        # Try exact normalized match first
        if name_norm in self._name_index:
            return self._name_index[name_norm][0]

        # Try partial match
        for m in self._monsters:
            if normalize_name(m["name"]) == name_norm:
                return m

        return None

    def filter_monsters(
        self,
        type: str | None = None,
        subtype: str | None = None,
        cr_min: float | None = None,
        cr_max: float | None = None,
        size: str | None = None,
        alignment: str | None = None,
        habitat: str | None = None,
        legendary: bool | None = None,
    ) -> list[dict]:
        """Filter monsters by various criteria. Returns summaries."""
        results = []

        for m in self._monsters:
            if type is not None and normalize_text(m["type"]) != normalize_text(type):
                continue
            if subtype is not None and normalize_text(m.get("subtype") or "") != normalize_text(subtype):
                continue
            if cr_min is not None and m["cr_numeric"] < cr_min:
                continue
            if cr_max is not None and m["cr_numeric"] > cr_max:
                continue
            if size is not None:
                size_norm = normalize_text(size)
                m_size_norm = normalize_text(m["size"])
                # Handle "Mediano o Pequeño" matching either "Mediano" or "Pequeño"
                if size_norm in m_size_norm or m_size_norm in size_norm:
                    pass
                else:
                    continue
            if alignment is not None:
                align_norm = normalize_text(alignment)
                m_align_norm = normalize_text(m["alignment"])
                if align_norm not in m_align_norm and m_align_norm not in align_norm:
                    continue
            if habitat is not None:
                hab_norm = normalize_text(habitat)
                m_habitats = [normalize_text(h) for h in m.get("habitat", [])]
                if hab_norm not in m_habitats:
                    continue
            if legendary is not None:
                is_legendary = m["legendary_resistances"] > 0 or len(m.get("legendary_actions", [])) > 0
                if is_legendary != legendary:
                    continue

            results.append(self._summary(m))

        return results

    def list_types(self) -> list[str]:
        """Return sorted list of all monster types."""
        return self._types

    def list_sizes(self) -> list[str]:
        """Return sorted list of all sizes."""
        return self._sizes

    def list_alignments(self) -> list[str]:
        """Return sorted list of all alignments."""
        return self._alignments

    def list_crs(self) -> list[str]:
        """Return sorted list of all CR values."""
        return self._crs

    def list_habitats(self) -> list[str]:
        """Return sorted list of all habitats."""
        return self._habitats

    def count(self) -> int:
        """Return total number of monsters."""
        return len(self._monsters)

    def _summary(self, m: dict) -> dict:
        """Return a summary dict with only key fields."""
        return {
            "name": m["name"],
            "name_en": m.get("name_en", ""),
            "type": m["type"],
            "subtype": m.get("subtype"),
            "size": m["size"],
            "alignment": m["alignment"],
            "ac": m["ac"],
            "hp": m["hp"],
            "cr": m["cr"],
            "cr_numeric": m["cr_numeric"],
            "languages": m.get("languages", ""),
            "habitat": m.get("habitat", []),
            "source": m.get("source", ""),
            "legendary": m["legendary_resistances"] > 0 or len(m.get("legendary_actions", [])) > 0,
        }
