from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Feat:
    nombre: str
    categoria: str
    prerequisitos_raw: str
    nivel_requerido: int | None
    atributos_requeridos: list[str]
    repetible: bool
    descripcion: str
    beneficios: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "categoria": self.categoria,
            "prerequisitos_raw": self.prerequisitos_raw,
            "nivel_requerido": self.nivel_requerido,
            "atributos_requeridos": self.atributos_requeridos,
            "repetible": self.repetible,
            "descripcion": self.descripcion,
            "beneficios": self.beneficios,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Feat:
        return cls(
            nombre=d["nombre"],
            categoria=d["categoria"],
            prerequisitos_raw=d["prerequisitos_raw"],
            nivel_requerido=d["nivel_requerido"],
            atributos_requeridos=d["atributos_requeridos"],
            repetible=d["repetible"],
            descripcion=d["descripcion"],
            beneficios=d["beneficios"],
        )
