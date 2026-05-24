from typing import Iterable
from thefuzz import fuzz, process

from src.parser import MagicItem


FUZZY_THRESHOLD = 75


class SearchEngine:
    def __init__(self, items: Iterable[MagicItem]):
        self._items = list(items)

    def search(
        self,
        nombre: str | None = None,
        tipo: str | None = None,
        rareza: str | None = None,
        requiere_sintonizacion: bool | None = None,
    ) -> list[MagicItem]:
        results = self._items

        if tipo is not None:
            tipo_lower = tipo.lower()
            results = [i for i in results if i["tipo"].lower() == tipo_lower]

        if rareza is not None:
            rareza_lower = rareza.lower()
            results = [i for i in results if rareza_lower in i["rareza"].lower()]

        if requiere_sintonizacion is not None:
            results = [i for i in results if i["requiere_sintonizacion"] == requiere_sintonizacion]

        if nombre is not None:
            nombre_lower = nombre.lower()
            scored = []
            for item in results:
                name_lower = item["nombre"].lower()
                ratio = fuzz.partial_ratio(nombre_lower, name_lower)
                if ratio >= FUZZY_THRESHOLD:
                    scored.append((ratio, item))
            scored.sort(key=lambda x: -x[0])
            results = [item for _, item in scored]

        return results

    def get(self, nombre: str) -> MagicItem | None:
        nombre_lower = nombre.lower()
        names = [item["nombre"].lower() for item in self._items]

        # Try exact match first
        for i, name in enumerate(names):
            if name == nombre_lower:
                return self._items[i]

        # Fuzzy match
        best_match = process.extractOne(nombre_lower, names, scorer=fuzz.ratio)
        if best_match:
            match_name, score = best_match
            if score >= FUZZY_THRESHOLD:
                idx = names.index(match_name)
                return self._items[idx]

        return None

    def list_types(self) -> list[str]:
        tipos = sorted({i["tipo"] for i in self._items})
        return tipos

    def list_rarities(self) -> list[str]:
        seen = set()
        for item in self._items:
            seen.add(item["rareza"])
        return sorted(seen)
