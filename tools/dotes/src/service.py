from __future__ import annotations

from src.models import Feat


class FeatService:
    def __init__(self, feats: list[Feat]):
        self._feats = feats

    def buscar_dotes(self, query: str) -> list[Feat]:
        if not query.strip():
            return list(self._feats)
        q = query.strip().lower()
        return [f for f in self._feats if q in f.nombre.lower()]

    def listar_dotes(
        self,
        categoria: str | None = None,
        atributo: str | None = None,
        nivel_max: int | None = None,
        buscar_texto: str | None = None,
    ) -> list[Feat]:
        results = list(self._feats)

        if categoria is not None:
            results = [f for f in results if f.categoria == categoria]

        if atributo is not None:
            attr_lower = atributo.strip().lower()
            results = [
                f
                for f in results
                if any(a.lower() == attr_lower for a in f.atributos_requeridos)
            ]

        if nivel_max is not None:
            results = [
                f
                for f in results
                if f.nivel_requerido is None or f.nivel_requerido <= nivel_max
            ]

        if buscar_texto is not None and buscar_texto.strip():
            q = buscar_texto.strip().lower()
            results = [
                f
                for f in results
                if q in f.nombre.lower()
                or q in f.descripcion.lower()
            ]

        return results

    def detalle_dote(self, nombre: str) -> Feat | None:
        nombre_lower = nombre.strip().lower()
        for f in self._feats:
            if f.nombre.lower() == nombre_lower:
                return f
        return None

    def listar_categorias(self) -> list[str]:
        seen = {}
        for f in self._feats:
            if f.categoria not in seen:
                seen[f.categoria] = None
        return list(seen.keys())
