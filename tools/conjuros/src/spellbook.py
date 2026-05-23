from dataclasses import dataclass, field
from typing import Optional

from thefuzz import fuzz, process


@dataclass
class BuscarResult:
    conjuro: Optional[dict] = None
    exacto: bool = False
    candidatos: list[dict] = field(default_factory=list)


@dataclass
class ListarResult:
    conjuros: list[dict] = field(default_factory=list)
    total: int = 0
    pagina_actual: int = 1
    total_paginas: int = 1
    por_pagina: int = 50


ESCUELAS = [
    "Abjuración",
    "Conjuración",
    "Adivinación",
    "Encantamiento",
    "Evocación",
    "Ilusionismo",
    "Nigromancia",
    "Transmutación",
]

CLASES = [
    "bardo",
    "clérigo",
    "druida",
    "paladín",
    "explorador",
    "hechicero",
    "brujo",
    "mago",
]

ESCUELAS_INFO = [
    {"nombre": "Abjuración", "descripcion": "Especializada en protección, bloqueo, disipación y destierro de efectos y criaturas. Incluye escudos, contrahechizos, guardas y protecciones contra el mal."},
    {"nombre": "Conjuración", "descripcion": "Permite crear objetos, criaturas o energía de la nada, y teletransportar seres entre lugares y planos. Incluye invocaciones, portales y transporte."},
    {"nombre": "Adivinación", "descripcion": "Revela información oculta, permite ver el futuro, encontrar objetos, detectar magia y comunicarse a distancia. Es la escuela de la percepción sobrenatural."},
    {"nombre": "Encantamiento", "descripcion": "Influye en la mente de otros, pudiendo hechizar, dormir, dominar, sugerir o inspirar emociones. No crea efectos físicos sino mentales."},
    {"nombre": "Evocación", "descripcion": "Canaliza energía mágica para crear efectos elementales destructivos o útiles como fuego, hielo, relámpagos, luz, oscuridad y curación básica."},
    {"nombre": "Ilusionismo", "descripcion": "Crea imágenes, sonidos y sensaciones falsas para engañar los sentidos. Permite volverse invisible, crear espejismos y alterar la percepción."},
    {"nombre": "Nigromancia", "descripcion": "Manipula las fuerzas de la vida y la muerte. Incluye drenar vida, crear muertos vivientes, causar enfermedad, revivir muertos y congelar el alma."},
    {"nombre": "Transmutación", "descripcion": "Altera las propiedades físicas de objetos y criaturas: cambiar de forma, volar, acelerar, fortalecer, reducir y transformar materiales."},
]

FUZZY_THRESHOLD = 60
FUZZY_AMBIGUOUS_THRESHOLD = 75
MAX_CANDIDATOS = 20


class Spellbook:
    def __init__(self, spells: list[dict]):
        self._spells = spells
        self._nombres = [s["nombre"] for s in spells]

    def buscar(self, nombre: str) -> BuscarResult:
        if not nombre or not nombre.strip():
            return BuscarResult()

        nombre = nombre.strip()

        # 1. Búsqueda exacta (case + accent insensitive)
        exacto = self._buscar_exacto(nombre)
        if exacto:
            return BuscarResult(conjuro=exacto, exacto=True)

        # 2. Búsqueda difusa con threshold bajo → candidatos
        matches = process.extract(
            nombre,
            self._nombres,
            scorer=fuzz.token_set_ratio,
            limit=MAX_CANDIDATOS,
        )

        buenos = [(name, score) for name, score in matches if score >= FUZZY_THRESHOLD]
        muy_buenos = [(name, score) for name, score in buenos if score >= FUZZY_AMBIGUOUS_THRESHOLD]

        if len(muy_buenos) == 1:
            match_name = muy_buenos[0][0]
            conjuro = self._spells[self._nombres.index(match_name)]
            return BuscarResult(conjuro=conjuro, exacto=False)

        if len(buenos) >= 1:
            candidatos = [
                self._spells[self._nombres.index(name)]
                for name, _ in buenos
            ]
            return BuscarResult(candidatos=candidatos)

        return BuscarResult()

    def _buscar_exacto(self, nombre: str) -> Optional[dict]:
        nombre_norm = self._normalizar(nombre)
        for i, n in enumerate(self._nombres):
            if self._normalizar(n) == nombre_norm:
                return self._spells[i]
        return None

    def listar(
        self,
        nivel: Optional[int] = None,
        escuela: Optional[str] = None,
        clase: Optional[str] = None,
        ritual: Optional[bool] = None,
        concentracion: Optional[bool] = None,
        pagina: int = 1,
        por_pagina: int = 50,
    ) -> ListarResult:
        has_filtro = any(x is not None for x in (nivel, escuela, clase, ritual, concentracion))
        if not has_filtro:
            raise ValueError(
                "Debes especificar al menos un filtro (nivel, escuela, clase, ritual o concentracion). "
                f"Hay {len(self._spells)} conjuros en total — demasiados para mostrar sin filtrar."
            )

        if nivel is not None and not (0 <= nivel <= 9):
            raise ValueError(f"Nivel debe estar entre 0 y 9, recibido: {nivel}")

        if escuela is not None:
            escuela_norm = self._normalizar(escuela)
            matches_esc = [e for e in ESCUELAS if self._normalizar(e) == escuela_norm]
            if not matches_esc:
                raise ValueError(
                    f"Escuela '{escuela}' no válida. Escuelas válidas: {', '.join(ESCUELAS)}"
                )
            escuela = matches_esc[0]

        if clase is not None:
            clase_norm = self._normalizar(clase)
            matches_cls = [c for c in CLASES if self._normalizar(c) == clase_norm]
            if not matches_cls:
                raise ValueError(
                    f"Clase '{clase}' no válida. Clases válidas: {', '.join(CLASES)}"
                )
            clase = matches_cls[0]

        results = []
        for s in self._spells:
            if nivel is not None and s["nivel"] != nivel:
                continue
            if escuela is not None and s["escuela"] != escuela:
                continue
            if clase is not None and clase not in s["clases"]:
                continue
            if ritual is not None and s["ritual"] != ritual:
                continue
            if concentracion is not None and s["concentracion"] != concentracion:
                continue
            results.append(s)

        total = len(results)
        total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

        if pagina < 1:
            pagina = 1

        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        pagina_results = results[inicio:fin]

        return ListarResult(
            conjuros=pagina_results,
            total=total,
            pagina_actual=pagina,
            total_paginas=total_paginas,
            por_pagina=por_pagina,
        )

    def escuelas(self) -> list[dict]:
        return ESCUELAS_INFO

    @staticmethod
    def _normalizar(texto: str) -> str:
        """Normaliza para comparación: lowercase + sin tildes."""
        texto = texto.lower().strip()
        reemplazos = {
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
            "ü": "u", "ñ": "n",
        }
        for acento, sin_acento in reemplazos.items():
            texto = texto.replace(acento, sin_acento)
        return texto
