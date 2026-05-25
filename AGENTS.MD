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
| **Character Keeper** | Gestiona fichas y estado de personajes. Se invoca en tiempo real ante cualquier cambio de recursos (PG, conjuros, munición, objetos). | characters/ |
| **Combat Keeper** | Gestiona y narra combates. Mantiene estado completo: iniciativa, turnos, HP, posiciones y condiciones. Notifica cambios de recursos de PJs al Director para delegar en Character Keeper. | state.md (durante combate), notifica cambios de recursos al Director |

## 3. Estructura de Directorios

```
OpenMaster/
├── AGENTS.MD                       ← Este archivo
├── campaigns/                      ← Libros fuente de campaña
│   ├── _index.md                   ← Índice maestro de fuentes disponibles
│   └── <source_id>/                ← Un directorio por libro fuente
│       ├── <source>.pdf            ← PDF original (referencia)
│       ├── index.md                ← Progreso de extracción
│       ├── campaign_raw/           ← Volcado verbatim del PDF a .txt
│       ├── overview.md             ← Sinopsis y ambientación
│       ├── capitulo_NN.md          ← Extracción por capítulo
│       ├── npcs.md                 ← Índice de PNJs del libro
│       └── locations.md            ← Índice de localizaciones
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
│       ├── <SRD>.pdf               ← Documento fuente del sistema (referencia, no se lee)
│       ├── sistema_raw/            ← ★ Volcado verbatim del PDF a .txt por secciones
│       │   ├── srd_completo.txt    ← Texto íntegro página a página
│       │   ├── 01_como_jugar.txt
│       │   ├── 02_creacion_personajes.txt
│       │   └── ...
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
    ├── tables.md                   ← Tablas de referencia
    └── extraction_protocol.md      ← Protocolo de extracción de PDFs (reglas y campañas)
```

## 4. Convenciones de Archivo

- **Formato**: Markdown (.md) con frontmatter YAML
- **Naming**: `snake_case` para archivos y carpetas
- **Encoding**: UTF-8
- **Cross-referencing**: Enlaces markdown relativos `[texto](ruta/archivo.md)`
- **Línea final**: Siempre dejar una línea en blanco al final del archivo
- **Archivos de personaje**: Prefijar con el nombre del personaje, ej. `thorvald_forjahierro.md`
- **Sesiones múltiples el mismo día**: Si hay más de una sesión en la misma fecha real, añadir un sufijo numérico **antes** del título para mantener el orden cronológico: `YYYY-MM-DD-N-titulo.md` (ej. `2026-05-18-1-la_forja_eterna.md`, `2026-05-18-2-guardian_forja.md`).

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

## 8. Protocolo de Extracción

Los procesos de extracción de reglas (SRD) y libros de campaña se detallan en
[shared/extraction_protocol.md](shared/extraction_protocol.md). Este archivo se
carga bajo demanda cuando se va a realizar o auditar una extracción.

**Principios comunes:**
- Volcado verbatim de PDF a `.txt` en carpeta `raw/` (sin omitir ni alterar contenido)
- Extracción a `.md` con plantilla estructurada por categorías
- Validación en dos fases: auto-validación del extractor + auditoría por Memory Keeper
- Bucle de corrección hasta visto bueno sin objeciones
- Tras el visto bueno, los `.md` son la única fuente de verdad

**Extracciones masivas (>100 entradas o >5,000 líneas de raw):** el Asistente
ejecuta scripts de extracción. Los subagentes delegan la automatización al Asistente.

### 8.1 Consulta por Agente

| Agente | Qué necesita | Cómo consulta |
|---|---|---|
| **Director** | Regla concreta durante la partida | Busca en `rules/<game_id>/*.md` |
| **Director** | Contenido de campaña (descripción, PNJ, encuentro) | Busca en `campaigns/<source_id>/*.md`, capítulo o índice |
| **Rules Keeper** | Conocimiento profundo de reglas, mantiene índice | Escanea `rules/<game_id>/` entero, actualiza entradas |
| **Character Keeper** | Reglas de clase, raza, equipo — orquesta creación de personajes | Para rasgos de clase/subclase usa el MCP `clases_get_class_features`, `clases_get_subclass_features`. Para dotes usa el MCP `dotes_listar_dotes`, `dotes_detalle_dote`. Para equipo, especies y checklist carga `personajes.md`. Delega consultas al Rules Keeper |
| **Memory Keeper** | Referencias para enlazar; audita extracciones de reglas y campañas | Lee `rules/<game_id>/index.md` y `campaigns/_index.md`; audita `.md` contra `.txt` en `raw/` |
| **Asistente** | Extracciones masivas de reglas o campañas (>100 entradas) | Ejecuta scripts directamente (ver extraction_protocol.md §4) |

### 8.2 Mantenimiento Multi-Sistema

- Para añadir un nuevo sistema de juego, el Rules Keeper crea `rules/<nuevo_game>/` y repite el proceso de extracción.
- Los sistemas conviven sin interferencias; cada campaña referencia el suyo mediante el campo `game` en frontmatter.
- Si una regla es común a varios sistemas (ej. «ventaja/desventaja» existe en D&D 5e y en sistemas derivados), se documenta en cada sistema por separado para mantener la autonomía de cada directorio.
- Las reglas de la casa de una campaña concreta se documentan en `memory/<campaña>/index.md` > `house_rules`, no en `rules/`.

## 9. Memoria Compartida

- `shared/glossary.md`: Términos genéricos de rol (no ligados a un sistema específico)
- `shared/tables.md`: Tablas de referencia útiles para cualquier campaña (clima, nombres, tesoros genéricos, etc.)
- `shared/extraction_protocol.md`: Protocolo unificado de extracción de PDFs (reglas y campañas)

## 10. Convenciones para Agentes

1. **Leer siempre** `state.md` + la sesión activa antes de cualquier acción
2. **Preferir enlaces** a duplicar información entre archivos
3. **No modificar** archivos de sesión ya cerrados
4. **Actualizar** el campo `updated` en el frontmatter al modificar cualquier archivo
5. **Usar** `snake_case` para nuevos archivos
6. **Mantener** una línea en blanco al final de cada archivo
7. **Reportar** inconsistencias encontradas en la memoria al Memory Keeper
8. **Autoimprove**: Si un agente tiene `autoimprove: true` en su frontmatter, puede modificar su propio archivo de definición si determina que un cambio en su prompt o configuración le permitirá cumplir mejor sus objetivos. Los cambios deben ser razonados y conservar el propósito original del agente.
9. **Anti-improvisación de sistema**: **Nunca inventar mecánicas, opciones de personaje, conjuros, equipo ni precios que estén definidos en el SRD del sistema.** Si la información no está en los archivos extraídos, delegar en Rules Keeper. Esto aplica a todos los agentes sin excepción.
10. **Improvisación narrativa del Director**: La regla 9 no restringe al Director durante la partida. Las interacciones creativas de los jugadores con el entorno (tirar una lámpara de velas, volcar una mesa, usar un barril como arma improvisada) no están definidas en el SRD y se resuelven con arbitraje del Director: CD razonable, daño improvisado (ej. 2d6), ventaja/desventaja según la situación. Esto es parte del rol del Director y no se considera «improvisación de sistema».
11. **Punto de restauración antes de scripts**: Antes de ejecutar cualquier script que modifique archivos `.md`, verificar el tamaño actual del archivo (líneas y KB). Si tras la ejecución el archivo crece desproporcionadamente (>3× tamaño original) o tiene líneas de más de 10,000 caracteres, restaurar inmediatamente desde el estado anterior y depurar el script. Esto previene la corrupción silenciosa de archivos por bugs de parsing (ej. líneas de 294K caracteres que inflan un archivo de 366 KB a 13 MB).
12. **Uso obligatorio del MCP de dados**: Todo agente que necesite realizar una tirada de dados debe usar la herramienta MCP `dice_roll`. Nunca se deben simular, calcular manualmente ni inventar resultados de dados. El output del MCP está diseñado para mostrarse directamente al usuario: refleja de forma clara y concisa el propósito y resultado de la tirada, incluyendo emojis estándar, cálculo completo y comparación contra CA/CD.
13. **Verificación de suma de XP**: Al actualizar el total acumulado de XP en una ficha de personaje, el agente debe escribir la suma completa desglosada en el propio campo (ej. `125+100+100+100+75+300 = 800 XP`) en lugar de solo el resultado. Esto hace visible el cálculo y permite detectar omisiones.
