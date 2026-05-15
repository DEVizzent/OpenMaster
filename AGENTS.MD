# Sistema de Agentes para Dirección de Juegos de Rol

## 1. Overview

Sistema de agentes de IA para asistir o dirigir partidas de juegos de rol.
Arquitectura basada en memoria persistente en markdown con frontmatter YAML,
diseñada para ser agnóstica al sistema de juego.

## 2. Arquitectura de Agentes

Los agentes se definen por su rol. Cada agente tiene acceso de lectura a toda
la memoria y responsabilidades de escritura específicas.

| Agente | Rol | Escribe |
|---|---|---|
| **Director** | Orquestador principal. Narra, interpreta PNJs, arbitra reglas | state.md, sesiones |
| **Asistente** | Asistente virtual del DM. Documenta, consulta reglas y memoria, genera contenido | Consultas y notas (no escribe archivos de campaña directamente) |
| **Rules Keeper** | Consulta y aplica el sistema de reglas | rules/&lt;game_id&gt;/*.md |
| **Memory Keeper** | Gestiona la memoria persistente de campaña | Toda la memoria excepto sesiones |
| **Character Keeper** | Gestiona fichas y estado de personajes | characters/ |
| **Combat Keeper** | Gestiona y narra combates. Iniciativa, turnos, HP | state.md (solo durante combate) |

## 3. Estructura de Directorios

```
OpenMaster/
├── AGENTS.MD                       ← Este archivo
├── campaigns/                      ← Libros fuente de campaña
│   └── <nombre>.pdf|.md
├── memory/
│   ├── campaign_template/          ← Plantilla para nuevas campañas
│   └── <campaña-activa>/
│       ├── index.md                ← Ficha estática de campaña
│       ├── state.md                ← Resumen vivo del progreso
│       ├── characters/
│       │   ├── pcs/<nombre>.md     ← Personajes jugadores
│       │   └── npcs/<nombre>.md    ← PNJs
│       ├── places/<nombre>.md      ← Localizaciones
│       ├── sessions/
│       │   ├── _index.md           ← Timeline cronológico
│       │   └── YYYY-MM-DD-titulo.md
│       ├── factions/<nombre>.md    ← Organizaciones
│       └── quests/<nombre>.md      ← Misiones y arcos
├── rules/
│   ├── index.md                    ← Índice maestro de sistemas disponibles
│   └── <game_id>/                  ← Un directorio por sistema de juego
│       ├── <SRD>.pdf               ← Documento fuente del sistema
│       ├── index.md                ← Índice del sistema con progreso de extracción
│       └── <categoria>.md          ← Reglas extraídas por categoría
├── .opencode/
│   ├── opencode.json               ← Configuración de opencode
│   └── agents/
│       ├── director.md             ← Agente primario (orquestador)
│       ├── asistente.md            ← Agente primario (asistente DM)
│       ├── rules_keeper.md         ← Subagente de reglas
│       ├── memory_keeper.md        ← Subagente de memoria
│       ├── character_keeper.md     ← Subagente de personajes
│       └── combat_keeper.md        ← Subagente de combate
└── shared/
    ├── glossary.md                 ← Términos comunes de rol
    └── tables.md                   ← Tablas de referencia
```

## 4. Convenciones de Archivo

- **Formato**: Markdown (.md) con frontmatter YAML
- **Naming**: `snake_case` para archivos y carpetas
- **Encoding**: UTF-8
- **Cross-referencing**: Enlaces markdown relativos `[texto](ruta/archivo.md)`
- **Línea final**: Siempre dejar una línea en blanco al final del archivo
- **Archivos de personaje**: Prefijar con el nombre del personaje, ej. `thorvald_forjahierro.md`

## 5. Frontmatter — Campos Comunes

Todo archivo de memoria debe incluir estos campos en su frontmatter YAML:

```yaml
---
type: [campaign|character|place|session|faction|quest|state|session_index]
game: dnd_5e                      # Identificador del sistema de juego
campaign: nombre_campania         # Nombre de la campaña (snake_case)
created: 2026-05-13               # Fecha de creación (YYYY-MM-DD)
updated: 2026-05-13               # Fecha de última modificación
tags: [tag1, tag2]                # Etiquetas libres para búsqueda
---
```

## 6. Tipos de Memoria — Esquemas

### 6.1 Campaign (`index.md`)

```yaml
---
type: campaign
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `title` | string | Nombre de la campaña |
| `source` | string | Ruta al libro fuente en `campaigns/` |
| `world` | text | Resumen del mundo y ambientación |
| `tone` | string | Tono de la partida (épico, oscuro, humor, etc.) |
| `players` | list | Lista de jugadores y sus personajes |
| `house_rules` | list | Reglas de la casa, si las hay |
| `narrative_style` | string | Estilo narrativo (funcional, equilibrado, detallado, barroco) |
| `age_rating` | string | Clasificación por edad (+18, +16, +12, todos) |
| `lines` | list | Líneas rojas — temas que no ocurren bajo ninguna circunstancia |
| `veils` | list | Velos — temas que pueden ocurrir pero no se describen en escena |
| `expectations` | text | Expectativas del grupo: combate vs rol, lineal vs sandbox, etc. |
| `narrative_control` | num | Control narrativo del jugador (0 solo mecánico — 10 narración completa) |
| `notes` | text | Notas generales del director |

> **Nota sobre escalabilidad**: Si `index.md` crece hasta volverse difícil de mantener, estos campos de contrato social (narrative_style, age_rating, lines, veils, expectations, narrative_control) pueden extraerse a un archivo independiente `campaign_compact.md` en la raíz de la campaña, manteniendo la separación entre lore del mundo y acuerdo de grupo.

### 6.2 State (`state.md`)

```yaml
---
type: state
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `current_date` | string | Fecha y hora actual en el mundo |
| `party_location` | link | Lugar actual del grupo |
| `active_quests` | list | Quest activas con enlaces a `quests/` |
| `recent_events` | text | Resumen de 2-4 líneas de lo último relevante |
| `party_status` | text | Estado del grupo (heridas, recursos, descansos) |
| `pending_decisions` | list | Decisiones que dejó el grupo sin resolver |
| `next_session_hook` | text | Gancho para arrancar la siguiente sesión |
| `notable_changes` | list | Impacto de los PJs en el mundo |
| `downtime` | list | Acciones de descanso en curso |

### 6.3 Character (`characters/pcs/<nombre>.md` o `characters/npcs/<nombre>.md`)

```yaml
---
type: character
kind: pc|npc
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | string | Nombre completo |
| `player` | string | (solo pc) Nombre del jugador |
| `species` | string | Raza / especie |
| `class` | string | Clase y nivel |
| `role` | string | Rol en el grupo |
| `location` | link | Lugar actual |
| `status` | string | Vivo, herido, muerto, desaparecido, etc. |
| `description` | text | Apariencia y personalidad |
| `backstory` | text | Historia resumida |
| `goals` | list | Motivaciones del personaje |
| `relationships` | list | Relaciones con otros personajes o entidades |
| `inventory` | list | Objetos relevantes |
| `notes` | text | Notas libres de la partida |

### 6.4 Place (`places/<nombre>.md`)

```yaml
---
type: place
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | string | Nombre del lugar |
| `region` | string | Región o área |
| `description` | text | Descripción general |
| `notable_features` | list | Puntos de interés |
| `npcs` | list | PNJs presentes con enlaces |
| `shops` | list | Comercios y servicios |
| `connections` | list | Conexiones a otros lugares |
| `danger_level` | string | Peligrosidad (baja, media, alta, letal) |

### 6.5 Session (`sessions/YYYY-MM-DD-titulo.md`)

```yaml
---
type: session
session_number: N
date_played: 2026-05-13
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `title` | string | Título de la sesión |
| `date_ingame` | string | Fecha en el mundo de juego |
| `party_present` | list | PJs presentes con enlaces |
| `summary` | text | Resumen detallado de lo ocurrido |
| `npcs_met` | list | PNJs nuevos encontrados |
| `places_visited` | list | Lugares visitados |
| `items_found` | list | Objetos conseguidos |
| `decisions` | list | Decisiones importantes del grupo |
| `cliffhanger` | text | Punto final o cliffhanger |
| `xp_gained` | string | Experiencia obtenida (si aplica) |

### 6.6 Session Index (`sessions/_index.md`)

```yaml
---
type: session_index
---
```

Tabla cronológica de todas las sesiones:

| # | Fecha real | Fecha in-game | Título | Resumen |
|---|---|---|---|---|

### 6.7 Faction (`factions/<nombre>.md`)

```yaml
---
type: faction
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | string | Nombre de la organización |
| `type` | string | Tipo (gremio, culto, nobleza, orden, etc.) |
| `goals` | list | Objetivos de la organización |
| `leadership` | list | Líderes conocidos |
| `members` | list | Miembros conocidos con enlaces |
| `base` | link | Cuartel general |
| `reputation` | num | Reputación con el grupo (-5 a +5) |
| `secrets` | list | Secretos (solo para el director) |
| `notes` | text | Notas del director |

### 6.8 Quest (`quests/<nombre>.md`)

```yaml
---
type: quest
status: active|completed|failed|pending
---
```

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | string | Nombre de la misión o arco |
| `giver` | link | Quién la otorga (PNJ o facción) |
| `type` | string | Tipo (principal, secundaria, personal, arco) |
| `objectives` | list | Objetivos con estado [pendiente/completado/fallido] |
| `rewards` | list | Recompensa ofrecida |
| `deadline` | string | Fecha límite in-game |
| `related_npcs` | list | PNJs relacionados |
| `related_places` | list | Lugares relacionados |
| `notes` | text | Notas del director |

## 7. Protocolo de Ciclo de Vida

### 7.1 Inicio de Campaña (Session 0)

Antes de la primera sesión, dos procesos se ejecutan **en paralelo** para minimizar la espera:

| Agente | Tarea | Genera |
|---|---|---|
| **Rules Keeper** | Extrae el SRD del sistema de juego | `rules/<game_id>/*.md` |
| **Director** | Realiza la batería de preguntas a los jugadores | Actualiza `index.md` con compact |

Cuando ambos procesos finalizan, el Memory Keeper puede crear la campaña en `memory/<campaña>/` con todo el contexto listo.

### 7.2 Inicio de Sesión

1. Memory Keeper crea el archivo de sesión en `sessions/` con el formato `YYYY-MM-DD-titulo_breve.md`
2. Se copia el `state.md` actual como sección inicial de contexto
3. Los agentes cargan `state.md` + última sesión para contexto

### 7.3 Durante la partida

- Los agentes leen `state.md` para mantener coherencia
- El Director puede actualizar `state.md` si ocurre un cambio crítico (ubicación, estado del grupo)
- Los agentes referencian información mediante enlaces relativos, sin duplicar datos

### 7.4 Cierre de sesión

Al terminar la sesión se deben actualizar:

1. **Archivo de sesión**: Completar secciones (summary, decisions, cliffhanger, etc.)
2. **`state.md`**: Reflejar el nuevo estado (fecha, ubicación, quests activas, eventos recientes, hook)
3. **`sessions/_index.md`**: Añadir entrada en la tabla cronológica
4. **Personajes**: Actualizar si hubo cambios (nivel, equipo, estado, relaciones)
5. **Lugares/PNJs/Facciones/Quests**: Actualizar si aplica

### 7.5 Post-partida

- No modificar archivos de sesión ya cerrados
- Para correcciones o retrocontinuidad, añadir una nota al inicio del archivo de sesión con fecha de la corrección
- Los cambios al mundo fuera de sesión se registran en `state.md` > `notable_changes`

## 8. Protocolo de Extracción y Consulta de Reglas

### 8.1 Organización de Archivos

Cada sistema de juego tiene su propio directorio en `rules/<game_id>/`. Un sistema se identifica por su `game_id` (ej. `dnd_5e`, `cypher`, `call_of_cthulhu`).

```
rules/
├── index.md                    ← Índice maestro: lista sistemas disponibles
│                                 y enlaces a cada rules/<game_id>/index.md
└── <game_id>/
    ├── index.md                ← Índice del sistema con progreso de extracción
    ├── <SRD>.pdf               ← Documento fuente original
    ├── reglas_basicas.md       ← Reglas extraídas por categoría
    ├── combate.md
    ├── magia.md
    ├── personajes.md
    └── direccion.md
```

- `rules/index.md` (raíz) contiene solo la lista de sistemas disponibles y enlaces.
- Cada `rules/<game_id>/index.md` contiene el índice detallado con checkboxes de progreso.
- Cada categoría se extrae a su propio archivo `<categoria>.md` para facilitar la consulta por agentes.
- El campo `game` en el frontmatter identifica el sistema en cada archivo.

### 8.2 Plantilla de Entrada Extraída

Cada regla extraída dentro de un archivo de categoría debe seguir este formato:

```markdown
### [Nombre de la regla]
- **Fuente**: `<SRD>.pdf`, pág. XX, sección Y
- **Tags**: `#tag1 #tag2`
- **Regla**: Texto conciso de la mecánica. Incluir valores numéricos, dados,
  CD, condiciones, etc.
- **Relacionado**: [regla relacionada](combate.md#regla)
```

**Ejemplo real:**

```markdown
### Caída
- **Fuente**: `SP_SRD_CC_v5.2.1.pdf`, pág. 67, sección «Caída»
- **Tags**: `#combate #dano #movimiento`
- **Regla**: Una criatura recibe 1d6 de daño contundente por cada 3 metros
  de caída, hasta un máximo de 20d6. La criatura cae tumbada si recibe daño.
- **Relacionado**: [daño por caída](combate.md#dano)
```

**Requisito adicional para `personajes.md`**: Al final del archivo, incluir siempre una sección «Checklist de creación completa» con todos los elementos necesarios para dar un personaje como creado en ese sistema. El Character Keeper usará este checklist para no olvidar ningún paso durante la creación:

```markdown
## Checklist de creación completa
- [ ] [Elemento requerido 1]
- [ ] [Elemento requerido 2]
...
- [ ] Nombre y backstory
```

### 8.3 Proceso de Extracción

1. **Escaneo inicial**: Leer la tabla de contenidos del SRD y mapear las secciones a las categorías definidas en el índice.
2. **Creación de archivos**: Para cada categoría, crear `rules/<game_id>/<categoria>.md`.
3. **Extracción**: Por cada regla dentro de la sección, escribir una entrada siguiendo la plantilla 8.2.
4. **Checklist de creación**: Para `personajes.md`, extraer también la lista completa de elementos que constituyen un personaje completo en este sistema (características, competencias, equipo, etc.). El Character Keeper usará este checklist durante la creación para no olvidar ningún paso.
5. **Indexado**: Marcar casillas en `rules/<game_id>/index.md` a medida que se completan categorías.
5. **Validación**: Verificar que todos los enlaces cruzados entre reglas apuntan a archivos y anclas existentes.
6. **Actualización de raíz**: Si el sistema es nuevo, añadirlo a `rules/index.md`.

### 8.4 Consulta por Agente

| Agente | Qué necesita | Cómo consulta |
|---|---|---|
| **Director** | Consulta rápida durante la partida (una regla concreta) | Busca por palabra clave en `rules/<game_id>/*.md` |
| **Rules Keeper** | Conocimiento profundo, mantiene el índice | Escanea `rules/<game_id>/` entero, actualiza entradas |
| **Character Keeper** | Reglas de clase, raza, equipo, dotes | Filtra por tags (`#clase #guerrero`) en `personajes.md` |
| **Memory Keeper** | Solo referencias para enlazar desde la memoria | Lee `rules/<game_id>/index.md` |

### 8.5 Mantenimiento Multi-Sistema

- Para añadir un nuevo sistema de juego, el Rules Keeper crea `rules/<nuevo_game>/` y repite el proceso 8.3.
- Los sistemas conviven sin interferencias; cada campaña referencia el suyo mediante el campo `game` en frontmatter.
- Si una regla es común a varios sistemas (ej. «ventaja/desventaja» existe en D&D 5e y en sistemas derivados), se documenta en cada sistema por separado para mantener la autonomía de cada directorio.
- Las reglas de la casa de una campaña concreta se documentan en `memory/<campaña>/index.md` > `house_rules`, no en `rules/`.

## 9. Memoria Compartida

- `shared/glossary.md`: Términos genéricos de rol (no ligados a un sistema específico)
- `shared/tables.md`: Tablas de referencia útiles para cualquier campaña (clima, nombres, tesoros genéricos, etc.)

## 10. Convenciones para Agentes

1. **Leer siempre** `state.md` + la sesión activa antes de cualquier acción
2. **Preferir enlaces** a duplicar información entre archivos
3. **No modificar** archivos de sesión ya cerrados
4. **Actualizar** el campo `updated` en el frontmatter al modificar cualquier archivo
5. **Usar** `snake_case` para nuevos archivos
6. **Mantener** una línea en blanco al final de cada archivo
7. **Reportar** inconsistencias encontradas en la memoria al Memory Keeper
8. **Autoimprove**: Si un agente tiene `autoimprove: true` en su frontmatter, puede modificar su propio archivo de definición si determina que un cambio en su prompt o configuración le permitirá cumplir mejor sus objetivos. Los cambios deben ser razonados y conservar el propósito original del agente.

## 11. Protocolo de Inicio de Campaña (Session 0)

### 11.1 Batería de Preguntas para Jugadores

El Director realiza las siguientes preguntas a los jugadores (verbalmente o mediante cuestionario). Las respuestas se registran en `memory/<campaña>/index.md` como parte del campaign compact.

| # | Pregunta | Propósito |
|---|---|---|
| 1 | ¿Qué estilo narrativo prefieres? (funcional, equilibrado, detallado, barroco) | Definir `narrative_style` |
| 2 | ¿Hay temas que quieras que no aparezcan en la partida? (violencia infantil, tortura, arañas, etc.) | Definir `lines` |
| 3 | ¿Hay temas que puedan aparecer pero no quieras que se describan en escena? | Definir `veils` |
| 4 | ¿Qué tono te apetece? (épico, oscuro, humorístico, intriga, supervivencia) | Definir `tone` |
| 5 | ¿Qué porcentaje de combate vs rol social te gustaría? | Definir `expectations` |
| 6 | ¿Prefieres una aventura lineal o sandbox? | Definir `expectations` |
| 7 | ¿Qué edad tienes? (para adecuar contenido) | Definir `age_rating` |
| 8 | ¿Qué esperas de esta campaña? ¿Algo que te gustaría explorar? | Definir `expectations` |

### 11.2 Estilo Narrativo

Define el nivel de detalle de las descripciones durante la partida:

| Valor | Significado |
|---|---|
| `funcional` | Descripciones mínimas («Entras en la cueva. Hay un goblin.»). Máximo ritmo de juego. |
| `equilibrado` | Descripciones moderadas. Ambiente sin ralentizar. |
| `detallado` | Descripciones ricas. Se busca inmersión sensorial. |
| `barroco` | Descripciones muy elaboradas. La narración es parte central de la experiencia. |

### 11.3 Líneas y Velos

Tomado de la técnica *Lines & Veils* de la comunidad de rol:

- **Línea (Line)**: El tema no aparece en la partida bajo ninguna circunstancia. Se respeta siempre.
- **Velo (Veil)**: El tema puede ocurrir pero ocurre *fuera de escena*. No se describe; se salta o se resume («lo que pasa en esa habitación no se cuenta»).

Ejemplos comunes:
- Violencia sexual → suele ser línea o velo (según grupo)
- Tortura explícita → línea común
- Aracnofobia → línea si hay jugadores con fobia
- Muerte de PNJs queridos → velo (se sabe que ocurre, no se describe)

### 11.4 Edad y Clasificación

| `age_rating` | Qué implica |
|---|---|
| `+18` | Sin restricciones. Violencia, horror, temas adultos permitidos. |
| `+16` | Violencia moderada. Sin sexo explícito ni gore gratuito. |
| `+12` | Violencia ligera y fantástica. Sin horror psicológico. |
| `todos` | Aventura ligera. Sin sangre, sin muerte gráfica, sin temas adultos. |

### 11.5 Tono y Expectativas

El tono define la atmósfera general y puede evolucionar:

- **Épico**: Hazañas, heroísmo, escalas grandes.
- **Oscuro**: Peligro real, moralidad gris, consecuencias duras.
- **Humorístico**: Situaciones cómicas, tono ligero, cuarta pared flexible.
- **Intriga**: Misterio, política, secretos, manipulación.
- **Supervivencia**: Recursos limitados, entorno hostil, gestión.

Las expectativas se documentan como texto libre en `expectations`. El control narrativo (`narrative_control`) es un valor 0-10 que define quién narra las acciones del personaje del jugador (ver sección 13.2).

### 11.6 Generación del campaign_compact

Las respuestas de la batería de preguntas se registran en `index.md` de la campaña:

```yaml
---
type: campaign
# ... campos comunes ...
narrative_style: equilibrado
age_rating: +18
lines: [violencia sexual, tortura]
veils: [muerte de PNJs]
tone: épico
expectations: >
  60% combate / 40% rol. Dungeon crawling con momentos de
  interpretación. Los jugadores quieren explorar una trama
  de misterio ligada a los trasfondos.
---
```

### 11.7 Separación Futura

Si `index.md` crece hasta volverse difícil de mantener, los campos de contrato social (11.2 a 11.5) pueden extraerse a un archivo `memory/<campaña>/campaign_compact.md`. El campo `type: compact` en frontmatter identifica este nuevo tipo de archivo, y `index.md` lo referenciará mediante un enlace relativo.

> **Decisión de diseño**: Se comienza con todo en `index.md` para minimizar el número de archivos en la fase inicial. La separación es un paso de refactorización que se toma cuando el archivo supera un tamaño manejable o cuando un agente necesita leer el compact sin cargar el lore completo de campaña.

## 12. Protocolo de Creación de Personaje

### 12.1 Principios

- **Sistema-agnóstico**: El protocolo no menciona ninguna especie, clase ni atributo concretos. Los obtiene dinámicamente de `rules/<game_id>/personajes.md`.
- **Solo pregunta lo necesario**: Si el jugador ya dijo «enano», no preguntes «¿enano o elfo?».
- **Opciones, no catálogos**: Máximo 5 opciones por pregunta, con 1 línea de descripción.
- **Recomienda, no impongas**: Sugiere la mejor opción según el concepto, pero deja decidir.
- **Usa el checklist del sistema**: Carga la sección «Checklist de creación completa» de `rules/<game_id>/personajes.md` y marca los elementos a medida que se completan. Esto asegura que ningún paso se olvide.

### 12.2 Fases

**Fase 0 — Carga del sistema**

1. Lee el campo `game` de `memory/<campaña>/index.md`
2. Carga `rules/<game_id>/personajes.md`
3. Extrae la sección «Checklist de creación completa» como guía de pasos

**Fase 1 — Concepto libre**

1. Pide al jugador: «Describe en 2-4 frases el personaje que quieres jugar»
2. Analiza el texto extrayendo: especie, rol/clase, tono, personalidad, temas implícitos
3. Responde con: «He entendido que quieres un [X] que [Y]. ¿Es correcto?»

**Fase 2 — Refinamiento guiado**

1. Repasa el checklist: ¿qué falta?
2. Pregunta solo por lo NO definido. Cada pregunta:
   - Presenta 3-5 opciones del sistema con 1 línea de descripción
   - Recomienda la(s) más afín(es) al concepto
   - Permite al jugador pedir más detalle de cualquiera
3. Orden sugerido: especie → clase/rol → subtipo → atributos → trasfondo → equipo
4. Marca cada elemento en el checklist al completarlo

**Fase 3 — Mecánicas**

1. Guía la asignación de atributos/puntuaciones según el sistema
2. Selección de equipo inicial si aplica
3. Habilidades, competencias, conjuros si aplican
4. Validación: ¿el checklist está completo?

**Fase 4 — Narrativa**

1. Nombre, apariencia física, personalidad
2. Backstory breve (3-5 líneas)
3. Motivaciones y objetivos

**Fase 5 — Guardado**

1. Validar contra las reglas del sistema (delega en Rules Keeper si es necesario)
2. Guardar en `characters/pcs/<nombre_snake_case>.md`
3. Formato: frontmatter YAML + secciones según AGENTS.md sección 6.3
4. Confirmar al jugador: «Personaje creado: [nombre], [especie] [clase] nivel [N]. Ficha en [ruta]»

### 12.3 Ejemplo de interacción (D&D 5e)

```
JUGADOR: Quiero un enano guerrero que busca vengar
         a su clan, destruido por un dragón.

AGENTE:  He entendido: enano, guerrero, motivado
         por venganza contra dragones. ¿Correcto?

JUGADOR: Sí. ¿Qué tipo de guerrero puedo ser?

AGENTE:  Opciones para guerrero enano:
         1. Campeón — más críticos, muy resistente
         2. Maestro de batalla — maniobras tácticas
         3. Caballero arcano — mezcla magia y espada
         Por tu historia de venganza, te sugiero
         Campeón (resistencia) o Maestro de batalla
         (táctico). ¿Cuál te llama más?
```

## 13. Formato de Respuesta en Partida

### 13.1 Dos bloques de respuesta

Toda acción resuelta de un jugador se responde con dos bloques:

1. **Bloque narrativo**: Describe lo ocurrido según los campos de la campaña:
   - `narrative_style` — nivel de detalle (funcional, equilibrado, detallado, barroco)
   - `tone` — atmósfera (épico, oscuro, cómico, etc.)
   - `narrative_control` — cuánto narra el jugador vs el agente
   - `age_rating` — respeta líneas y velos

2. **Bloque mecánico**: Notación compacta con cálculo completo, emoji de resultado y efecto. El formato concreto depende del sistema de juego y se define en `rules/<game_id>/formato_mecanico.md`.

### 13.2 Control narrativo (`narrative_control`)

Valor de 0 a 10 definido en el campaign compact. Aplica solo a las acciones que el personaje del jugador realiza o recibe directamente.

| Rango | Comportamiento del agente |
|---|---|
| **0-3** | Solo bloque mecánico. El jugador narra todo lo de su PJ. |
| **4-6** | Narración breve del agente + bloque mecánico. A veces el agente pregunta al jugador cómo lo ha hecho: *«El esqueleto lanza su cimitarra pero falla el golpe. ¿Cómo lo has evitado?»* |
| **7-10** | Narración completa del agente. El jugador solo declara la acción y recibe la descripción. |

**Restricciones**:
- El jugador solo narra las acciones de **su propio personaje**. El resto de la escena (PNJs, entorno, consecuencias indirectas a otros) la narra siempre el agente.
- La narración del jugador **no puede contradecir el resultado mecánico**. Si el jugador describe algo inconsistente con los dados (ej. *«le corto la cabeza»* cuando el daño no fue letal), el agente ignora esa narración y toma el control.
- El agente aplica siempre el bloque mecánico tras cualquier narración, como registro verificable.

### 13.3 Códigos de emoji estándar

| Emoji | Significado | Uso |
|---|---|---|
| ✅ | Éxito | Tirada iguala o supera CD/CA |
| ❌ | Fallo | Tirada no alcanza CD/CA |
| 🎯 | Crítico | 20 natural (o equivalente del sistema) |
| 💀 | Pifia | 1 natural (o equivalente) |
| 🩸 | Daño | Pérdida de PG o heridas |
| 🔥 | Daño elemental | Fuego, rayo, ácido, etc. |
| 🛡️ | Defensa | Bloqueo, armadura, cobertura, resistencia |
| ✨ | Magia | Conjuro o efecto mágico |
| ☠️ | Estado | Condición aplicada (envenenado, asustado, etc.) |
| 💚 | Curación | Recuperación de PG o heridas |
| ⚡ | Reacción | Ataque de oportunidad, reacción usada |
| 📍 | Movimiento | Cambio de posición relevante |

### 13.4 Formato mecánico por sistema

Cada sistema define ejemplos concretos de su notación en `rules/<game_id>/formato_mecanico.md`. El agente debe cargar este archivo al inicio de la sesión para aplicar el formato correcto. Los emojis de la tabla 13.3 son estándar para todos los sistemas.
