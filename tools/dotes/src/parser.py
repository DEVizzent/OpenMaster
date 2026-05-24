from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from src.models import Feat

ATRIBUTOS = {"Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"}


class DotesParser:
    def parse_html(self, html: str) -> list[Feat]:
        soup = BeautifulSoup(html, "html.parser")
        feats = []
        for bloc in soup.select("div.bloc"):
            feat = self._parse_bloc(bloc)
            if feat:
                feats.append(feat)
        return feats

    def _parse_bloc(self, bloc: Tag) -> Feat | None:
        h1 = bloc.find("h1")
        if not h1:
            return None
        nombre = h1.get_text(strip=True)

        prereq_div = bloc.find("div", class_="prerequis")
        prerequisitos_raw = prereq_div.get_text(" ", strip=True) if prereq_div else ""

        categoria = self._extract_categoria(prerequisitos_raw)
        nivel_requerido = self._extract_nivel(prerequisitos_raw)
        atributos_requeridos = self._extract_atributos(prerequisitos_raw)

        desc_div = bloc.find("div", class_="description")
        resume = bloc.find("p", class_="resume")

        if desc_div:
            descripcion = desc_div.get_text(" ", strip=True)
            beneficios = self._extract_beneficios(desc_div)
            repetible = self._is_repetible(desc_div)
        elif resume:
            descripcion = resume.get_text(strip=True)
            beneficios = []
            repetible = False
        else:
            descripcion = ""
            beneficios = []
            repetible = False

        return Feat(
            nombre=nombre,
            categoria=categoria,
            prerequisitos_raw=prerequisitos_raw,
            nivel_requerido=nivel_requerido,
            atributos_requeridos=atributos_requeridos,
            repetible=repetible,
            descripcion=descripcion,
            beneficios=beneficios,
        )

    def _extract_categoria(self, prereq: str) -> str:
        lower = prereq.lower()
        if "dote de don épico" in lower:
            return "épico"
        if "dote de estilo de combate" in lower:
            return "estilo de combate"
        if "dote de origen" in lower:
            return "origen"
        if "dote general" in lower:
            return "general"
        return "general"

    def _extract_nivel(self, prereq: str) -> int | None:
        match = re.search(r"nivel (\d+)", prereq)
        if match:
            return int(match.group(1))
        return None

    def _extract_atributos(self, prereq: str) -> list[str]:
        match = re.search(r"nivel \d+ o más,\s*(.+?)$", prereq)
        if not match:
            return []
        remainder = match.group(1)
        # If the remainder contains "13 o más", extract attributes before it
        attr_match = re.match(r"(.+?)\s+13 o más", remainder)
        if not attr_match:
            return []
        attr_text = attr_match.group(1)
        # Split by " o " or ", " to get individual attributes
        parts = re.split(r"\s+o\s+|,\s*", attr_text)
        atributos = [p.strip() for p in parts if p.strip() in ATRIBUTOS]
        return atributos

    def _extract_beneficios(self, desc_div: Tag) -> list[str]:
        beneficios = []
        for strong in desc_div.find_all("strong"):
            text = strong.get_text(strip=True)
            if text and text.lower() not in ("repetible",):
                parent_text = strong.parent.get_text(" ", strip=True) if strong.parent else ""
                beneficios.append(parent_text)
        return beneficios

    def _is_repetible(self, desc_div: Tag) -> bool:
        for strong in desc_div.find_all("strong"):
            if strong.get_text(strip=True).lower() == "repetible":
                return True
        return False

    def parse_file(self, path: Path) -> list[Feat]:
        html = path.read_text(encoding="utf-8")
        return self.parse_html(html)

    def parse_and_save_json(self, html_path: Path, json_path: Path) -> None:
        feats = self.parse_file(html_path)
        data = [f.to_dict() for f in feats]
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            _json_dumps(data), encoding="utf-8"
        )


def _json_dumps(data: list[dict]) -> str:
    import json
    return json.dumps(data, ensure_ascii=False, indent=2)
