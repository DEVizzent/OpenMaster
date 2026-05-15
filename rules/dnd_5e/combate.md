---
type: rules
game: dnd_5e
created: 2026-05-15
updated: 2026-05-15
tags: [rules, dnd_5e, combat]
---

# Combate

Fuente: `SP_SRD_CC_v5.2.1.pdf`

---

### Estructura de un combate
- **Fuente**: pág. 14, sección «Estructura de un combate»
- **Tags**: `#combate #estructura #asaltos`
- **Regla**: El combate se organiza en asaltos (6 segundos in-game). Cada participante tiene un turno por asalto. Pasos: (1) Establecer posiciones, (2) Tirar iniciativa, (3) Turnarse. Si al terminar un asalto ningún bando ha sido derrotado, se pasa al siguiente.
- **Relacionado**: [iniciativa](combate.md#iniciativa)

---

### Iniciativa
- **Fuente**: pág. 14, sección «Iniciativa»
- **Tags**: `#combate #iniciativa #turnos`
- **Regla**: Al empezar el combate, todos los participantes hacen una prueba de Destreza para determinar el orden. El DM tira por los monstruos (una tirada por grupo de criaturas idénticas). **Sorpresa**: si un combatiente es sorprendido, tiene desventaja en la tirada de iniciativa. **Empates**: el DM decide entre monstruos, los jugadores deciden entre PCs.
- **Relacionado**: [turno](combate.md#tu-turno)

---

### Tu turno
- **Fuente**: pág. 14, sección «Tu turno»
- **Tags**: `#combate #turno #accion`
- **Regla**: En tu turno puedes moverte hasta tu velocidad y realizar una acción. Puedes comunicarte (frases cortas, gestos) sin coste. Puedes interactuar con un objeto/elemento sin coste. Puedes renunciar a moverte y/o actuar.
- **Relacionado**: [acciones](reglas_basicas.md#acciones-en-combate)

---

### Movimiento y posición
- **Fuente**: pág. 15, sección «Movimiento y posición»
- **Tags**: `#combate #movimiento #posicion`
- **Regla**: Puedes moverte hasta tu velocidad en tu turno. Puedes repartir el movimiento (antes y después de tu acción). **Terreno difícil**: cada metro cuesta 1 metro adicional. **Tamaño**: Diminuto (0,75 m), Pequeño/Mediano (1,5 m), Grande (3 m), Enorme (4,5 m), Gargantuesco (6 m). Tirarse al suelo: acción gratuita (estado derribado).
- **Relacionado**: [terreno difícil](combate.md#movimiento-y-posicion), [cobertura](combate.md#cobertura)

---

### Cobertura
- **Fuente**: pág. 16, sección «Cobertura»
- **Tags**: `#combate #cobertura #defensa`
- **Regla**: Tres niveles: **Media** (+2 a CA y salvaciones de Destreza, la cubre media criatura/objeto), **Tres cuartos** (+5 a CA y salvaciones de Destreza, objeto cubre 3/4), **Completa** (no puede ser objetivo directo de ataques ni conjuros). Solo se aplica el nivel más alto.
- **Relacionado**: [ataques a distancia](combate.md#ataques-a-distancia)

---

### Atacar
- **Fuente**: pág. 16, sección «Atacar»
- **Tags**: `#combate #ataque`
- **Regla**: Pasos del ataque: (1) Elegir objetivo (criatura, objeto o lugar), (2) Determinar modificadores (cobertura, ventaja/desventaja), (3) Resolver: tira el d20 de ataque, si aciertas tira el daño. **Ataques a distancia**: alcance normal (normal) y largo (desventaja). Si hay un enemigo a 1,5 m o menos, desventaja. **Ataque de oportunidad**: reacción cuando una criatura sale de tu alcance.
- **Relacionado**: [críticos](combate.md#criticos)

---

### Daño y curación
- **Fuente**: pág. 17, sección «Daño y curación»
- **Tags**: `#combate #dano #pg #curacion`
- **Regla**: **PG**: representan aguante físico. Al sufrir daño, réstalo de PG actuales. **Crítico** (20 natural): tira los dados de daño dos veces y suma. **Tipos de daño**: cortante, perforante, contundente, fuego, frío, etc. **Resistencia**: daño a la mitad. **Vulnerabilidad**: daño al doble. Se aplican en orden: ajustes → resistencias → vulnerabilidades. **Curación**: suma a PG actuales, no puede superar el máximo.
- **Relacionado**: [tiradas de salvación contra muerte](combate.md#tiradas-de-salvacion-contra-muerte)

---

### Tiradas de salvación contra muerte
- **Fuente**: pág. 19, sección «Llegar a 0 puntos de golpe»
- **Tags**: `#combate #muerte #salvacion`
- **Regla**: Cuando empiezas tu turno con 0 PG, tira 1d20 (sin modificadores). 10+ = éxito, 1-9 = fallo. Tres éxitos → estable. Tres fallos → mueres. 1 natural = 2 fallos. 20 natural = recuperas 1 PG. Estabilizar: prueba de Sabiduría (Medicina) CD 10. Una criatura estable recupera 1 PG tras 1d4 horas.
- **Relacionado**: [daño](combate.md#dano-y-curacion)

---

### Puntos de golpe temporales
- **Fuente**: pág. 20, sección «Puntos de golpe temporales»
- **Tags**: `#combate #pg #temporal`
- **Regla**: Los PG temporales se pierden primero al recibir daño. No se acumulan (elige mantener los actuales o los nuevos). Duran hasta consumirse o hasta un descanso largo. No son curación: con 0 PG, los PG temporales no te devuelven la consciencia.
- **Relacionado**: [daño](combate.md#dano-y-curacion)

---

### Atacantes y objetivos ocultos
- **Fuente**: pág. 16, sección «Atacantes y objetivos ocultos»
- **Tags**: `#combate #oculto #visibilidad`
- **Regla**: Si atacas a un objetivo al que no ves: desventaja. Si atacas a un objetivo que no te ve: ventaja. Si estás escondido al atacar, revelas tu posición (aciertes o no).
- **Relacionado**: [esconderse](reglas_basicas.md#exploracion)

---

### Agarrar
- **Fuente**: pág. 194, sección «Agarrar» (Glosario)
- **Tags**: `#combate #agarre`
- **Regla**: Puedes agarrar a una criatura con un ataque sin armas. Requiere una mano libre. El objetivo queda con el estado **agarrado** (velocidad 0, desventaja contra no-agarrador). Para escapar: acción, prueba de Fuerza (Atletismo) o Destreza (Acrobacias) contra tu CD. Puedes soltar gratis (sin acción).
- **Relacionado**: [agarrado](reglas_basicas.md#agarrado-estado)

---

### Áreas de efecto
- **Fuente**: pág. 195, sección «Área de efecto» (Glosario)
- **Tags**: `#combate #areas #conjuros`
- **Regla**: Formas de área: **Esfera** (punto de origen, radio), **Cono** (desde el lanzador, se ensancha), **Cubo** (desde un punto), **Cilindro** (radio y altura), **Línea** (trayectoria recta desde el origen hasta su alcance), **Emanación** (origen, el área se extiende en todas direcciones). El área de efecto cubre el espacio especificado. Para objetivos en el borde, el DM decide.
- **Relacionado**: [conjuros](magia.md#lanzamiento-de-conjuros)
