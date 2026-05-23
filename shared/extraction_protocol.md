---
type: protocol
created: 2026-05-19
updated: 2026-05-23
tags: [extraction, rules, campaigns, protocol]
---

# Protocolo de Extracción

Protocolo unificado para la extracción de reglas (SRDs) y libros de campaña
desde PDFs fuente. Se carga bajo demanda cuando un agente va a realizar,
auditar o corregir una extracción.

---

## 1. Principios Comunes

Estos principios aplican a cualquier extracción, sea de reglas o de campañas:

1. **Volcado verbatim**: El PDF se convierte a `.txt` sin omitir, resumir ni
   alterar ningún contenido. Cada palabra, tabla y valor numérico debe
   conservarse exactamente como está en el PDF fuente.
2. **Extracción estructurada**: Los `.txt` se procesan a `.md` siguiendo
   plantillas por tipo de contenido. El resultado es consultable por agentes.
3. **Validación en dos fases**: El agente extractor auto-valida (muestreo contra
   el `.txt` fuente). Luego el Memory Keeper audita de forma independiente.
4. **Bucle de corrección**: Si el Memory Keeper encuentra fallos, el extractor
   corrige y el Memory Keeper re-verifica. Se repite hasta visto bueno sin
   objeciones.
5. **Cierre**: Una vez validados, los archivos `.md` son la **única fuente de
   verdad**. Los `.txt` y el PDF no se consultan durante sesiones. Si durante
   la partida se detecta que falta información, se vuelve a los `.txt` para
   complementar, repitiendo validación.
6. **Punto de restauración antes de scripts**: Antes de ejecutar cualquier
   script que modifique `.md`, verificar tamaño actual (líneas y KB). Si tras
   la ejecución el archivo crece >3× o tiene líneas de >10,000 caracteres,
   restaurar y depurar el script.

---

## 2. Extracción de Reglas (SRD)

### 2.1 Organización de Archivos

Cada sistema de juego tiene su propio directorio en `rules/<game_id>/`.
Un sistema se identifica por su `game_id` (ej. `dnd_5e`, `cypher`).

```
rules/
├── index.md                    ← Índice maestro: lista sistemas disponibles
└── <game_id>/
    ├── index.md                ← Índice del sistema con progreso de extracción
    ├── <SRD>.pdf               ← Documento fuente original (referencia, no se lee)
    ├── sistema_raw/            ← Volcado verbatim del PDF a .txt por secciones
    │   ├── srd_completo.txt    ← Texto íntegro página a página
    │   ├── 01_como_jugar.txt
    │   ├── 02_creacion_personajes.txt
    │   └── ...
    ├── reglas_basicas.md       ← Reglas extraídas por categoría
    ├── combate.md
    ├── magia.md                      ← Reglas del sistema de magia (no catálogo — vía MCP)
    ├── personajes.md
    ├── direccion.md
    ├── objetos_magicos.md
    ├── bestiario.md
    └── formato_mecanico.md
```

- `rules/index.md` (raíz) contiene solo la lista de sistemas y enlaces.
- Cada `rules/<game_id>/index.md` contiene el índice con checkboxes de progreso.
- Cada categoría se extrae a su propio `<categoria>.md`.
- `sistema_raw/` es la fuente de verdad canónica para toda extracción.

### 2.2 Plantilla de Entrada Extraída (Reglas)

```markdown
### [Nombre de la regla]
- **Fuente**: `sistema_raw/<archivo>.txt`, PAGINA XX, sección Y
- **Versión**: SRD X.X (año)
- **Tags**: `#tag1 #tag2`
- **Regla**: Texto conciso de la mecánica. Incluir valores numéricos, dados,
  CD, condiciones, etc.
- **Relacionado**: [regla relacionada](combate.md#regla)
```

**Requisito adicional para `personajes.md`**: Al final del archivo, incluir
siempre una sección «Checklist de creación completa» con todos los elementos
necesarios para dar un personaje como creado en ese sistema.

### 2.3 Proceso de Extracción de Reglas

0. **Volcado a texto**: Convertir el PDF del SRD a `.txt` en
   `rules/<game_id>/sistema_raw/`. Un `srd_completo.txt` + archivos partidos
   por secciones lógicas.
1. **Escaneo inicial**: Leer la tabla de contenidos desde `sistema_raw/`,
   mapear secciones a categorías. Identificar la versión exacta del documento.
2. **Creación de archivos**: Para cada categoría, crear o actualizar
   `rules/<game_id>/<categoria>.md`.
3. **Extracción**: Por cada regla, leer del `.txt` en `sistema_raw/` y escribir
   una entrada siguiendo la plantilla 2.2. La extracción debe ser **completa** —
   no omitir subsecciones, variantes ni excepciones. Si una especie tiene
   sub-rasgos con opciones, extraer TODAS con sus valores mecánicos completos.
4. **Checklist de creación**: Para `personajes.md`, extraer la lista completa
   de elementos que constituyen un personaje completo en el sistema.
5. **Indexado**: Marcar checkboxes en `rules/<game_id>/index.md`.
6. **Validación**: Verificar enlaces cruzados. Revisar que cada entrada contenga
   todos los rasgos y valores del `.txt` fuente.

   **Checklist de auto-validación obligatorio** (antes del paso 7):
   - [ ] Muestrear 5 entradas por categoría: comparar valores numéricos contra el `.txt`
   - [ ] Verificar edición: confirmar que no hay valores de una edición anterior
   - [ ] Integridad de tablas: mismas filas, columnas y valores que en el `.txt`. Verificar al menos 2 columnas completas.
   - [ ] Longitud de líneas: ninguna línea > 5,000 caracteres
   - [ ] Tags correctos: formato `#categoria #subcategoria` sin errores ortográficos

7. **Verificación por Memory Keeper**: Audita los `.md` contra los `.txt` de
   `sistema_raw/`. Comprueba: (a) checklist de creación cubre todos los pasos,
   (b) cada categoría lista todas las opciones del SRD, (c) no hay omisiones de
   sub-rasgos o variantes, (d) no hay contradicciones entre archivos ni
   discrepancias de versión, (e) valores en tablas coinciden con el `.txt`.
8. **Bucle de corrección**: Si el Memory Keeper encuentra fallos, el
   **Rules Keeper corrige** y el **Memory Keeper re-verifica**. Se repite
   hasta visto bueno sin objeciones.
9. **Actualización de raíz**: Si el sistema es nuevo, añadirlo a `rules/index.md`.
10. **Cierre**: Los `.md` son la única fuente de verdad. Si durante la partida
    se detecta que falta información, el Rules Keeper vuelve a los `.txt` para
    complementar — y repite los pasos 6-8.

### 2.4 Mantenimiento Multi-Sistema

- Para añadir un nuevo sistema, el Rules Keeper crea `rules/<nuevo_game>/` y
  repite el proceso 2.3.
- Los sistemas conviven sin interferencias; cada campaña referencia el suyo
  mediante el campo `game` en frontmatter.
- Si una regla es común a varios sistemas, se documenta en cada sistema por
  separado para mantener la autonomía de cada directorio.
- Las reglas de la casa se documentan en `memory/<campaña>/index.md` >
  `house_rules`, no en `rules/`.

---

## 3. Extracción de Campañas

### 3.1 Organización de Archivos

Cada libro fuente de campaña tiene su propio directorio en `campaigns/<source_id>/`.
El `source_id` sigue la convención `snake_case` (ej. `curse_of_strahd`,
`lost_mine_of_phandelver`).

```
campaigns/
├── _index.md                       ← Índice maestro de fuentes de campaña
└── <source_id>/
    ├── <source>.pdf                ← PDF original (referencia, no se lee en partida)
    ├── index.md                    ← Índice con progreso de extracción
    ├── campaign_raw/               ← Volcado verbatim del PDF a .txt
    │   ├── completo.txt            ← Texto íntegro página a página
    │   ├── 00_introduccion.txt     ← Particionado por capítulos/secciones
    │   ├── 01_capitulo_1.txt
    │   └── ...
    ├── overview.md                 ← Sinopsis, ambientación, tono, trasfondo, mapa narrativo
    ├── capitulo_01.md              ← Extracción estructurada por capítulo
    ├── capitulo_02.md
    ├── ...
    ├── npcs.md                     ← Índice de todos los PNJs del libro (referencia cruzada)
    ├── locations.md                ← Índice de todas las localizaciones (referencia cruzada)
    ├── handouts.md                 ← Material para jugadores (cartas, mapas, descripciones)
    └── appendix.md                 ← Tablas, encuentros aleatorios, apéndices
```

- `campaigns/_index.md` (raíz) contiene solo la lista de fuentes y enlaces.
- Cada `campaigns/<source_id>/index.md` contiene el índice con checkboxes por
  capítulo y por categoría de índice (npcs, locations).
- Los capítulos se extraen a `capitulo_NN.md` con todo su contenido integrado
  (localizaciones, PNJs, encuentros, tesoros, puzles).
- `npcs.md` y `locations.md` son índices generados a partir de los capítulos,
  con enlaces al capítulo donde aparece cada elemento.
- `campaign_raw/` contiene el volcado verbatim, misma filosofía que `sistema_raw/`.
- **Los archivos extraídos en `campaigns/<source_id>/` son estáticos.**
  Una vez validados, no se modifican durante o después de las partidas. El estado
  vivo y las consecuencias de los PJs se registran exclusivamente en `memory/<campaña>/`.

### 3.2 Plantilla de Entrada Extraída (Campañas)

Cada elemento dentro de un capítulo sigue este formato:

```markdown
### [Nombre del elemento]
- **Fuente**: `campaign_raw/<archivo>.txt`, PÁGINA XX, sección Y
- **Tipo**: [location|npc|encounter|treasure|puzzle|lore]
- **Tags**: `#cripta #noMuerto #trampa`
- **Relevancia**: [principal|secundario|opcional]
- **Descripción**: Texto descriptivo completo, conservando todos los detalles
  del fuente.
- **En voz alta**: [solo si el libro provee boxed text para leer a jugadores]
  > Texto literal listo para leer a los jugadores, en bloque de cita markdown.
- **Stats**: [si aplica: CA, PG, ataques, CD de trampas, tiradas de salvación]
- **Tesoro**: [objetos, valores, ubicación exacta]
- **Desarrollo**: [sucesos que ocurren si los PJs interactúan, consecuencias,
  transiciones a otras áreas]
- **Conexiones**: [enlaces a otros elementos del libro o a `memory/`]
```

### 3.3 Plantilla de Entrada en Índices (npcs.md / locations.md)

Los índices contienen entradas breves con enlace al capítulo donde se desarrolla
cada elemento:

```markdown
### [Nombre del PNJ / localización]
- **Tipo**: [npc|location]
- **Capítulos**: [capitulo_01.md](capitulo_01.md), [capitulo_03.md](capitulo_03.md)
- **Rol**: [aliado|enemigo|neutral|nexo] / [ciudad|mazmorra|wilderness|plano]
- **Resumen**: Una línea descriptiva.
```

### 3.4 Proceso de Extracción de Campañas

0. **Volcado a texto**: Convertir el PDF de campaña a `.txt` verbatim en
   `campaigns/<source_id>/campaign_raw/`. Un `completo.txt` + archivos
   partidos por capítulos/secciones lógicas del libro.
1. **Escaneo inicial**: Leer la tabla de contenidos desde `campaign_raw/`.
   Mapear capítulos y secciones a los archivos de salida. Identificar el
   sistema de juego si el libro lo especifica.
2. **Creación de estructura**: Crear `index.md` con checkboxes de progreso
   por capítulo y por categoría de índice. Crear los archivos de capítulo
   vacíos y los índices.
3. **Extracción de capítulos**: Por cada capítulo, leer del `.txt` en
   `campaign_raw/` y extraer contenido a `capitulo_NN.md` siguiendo la
   plantilla 3.2. El boxed text se separa en bloques de cita markdown (`>`)
   para lectura en voz alta. Si el libro tiene >100 entradas de un tipo
   (PNJs, localizaciones), usar scripts de automatización (sección 4).
4. **Generación de índices**: Recorrer los capítulos extraídos y generar
   `npcs.md` y `locations.md` con entradas según la plantilla 3.3. Cada
   entrada enlaza al capítulo o capítulos donde aparece.
5. **Indexado**: Marcar checkboxes en `campaigns/<source_id>/index.md` a
   medida que se completan capítulos e índices.
6. **Validación**: Verificar enlaces entre capítulos e índices. Revisar que
   cada capítulo contenga todos los elementos que aparecen en el `.txt` fuente.

   **Checklist de auto-validación obligatorio** (antes del paso 7):
   - [ ] Muestrear 3 localizaciones y 3 PNJs contra el `.txt` fuente: ¿los valores (stats, tesoros, CDs) coinciden?
   - [ ] Verificar que el boxed text está correctamente identificado y separado en bloques de cita
   - [ ] Confirmar que todas las secciones del capítulo en el `.txt` tienen su correspondiente entrada en el `.md`
   - [ ] Longitud de líneas: ninguna línea > 5,000 caracteres
   - [ ] Tags correctos: formato `#categoria #subcategoria` sin errores ortográficos

7. **Verificación por Memory Keeper**: Audita los `.md` contra los `.txt` de
   `campaign_raw/`. Comprueba: (a) todos los capítulos están completamente
   extraídos, (b) los índices (`npcs.md`, `locations.md`) cubren todas las
   entradas de los capítulos, (c) no hay contradicciones entre capítulos
   (un mismo PNJ con nombres o stats distintos en capítulos diferentes),
   (d) el boxed text está correctamente identificado y el texto descriptivo
   preserva los detalles del fuente.
8. **Bucle de corrección**: Si el Memory Keeper encuentra fallos, el
   **Asistente corrige** y el **Memory Keeper re-verifica**. Se repite
   hasta visto bueno sin objeciones.
9. **Actualización de raíz**: Añadir entrada en `campaigns/_index.md`.
10. **Cierre**: Los `.md` son la única fuente de verdad. El PDF y los `.txt`
    de `campaign_raw/` no se consultan durante las sesiones. Si durante la
    partida se detecta que falta información, el Asistente vuelve a los `.txt`
    para complementar y repite los pasos 6-8.

### 3.5 Integración con Memoria de Campaña

El campo `source` en `memory/<campaña>/index.md` enlaza al directorio extraído:

```yaml
source: campaigns/curse_of_strahd/    # Enlace al directorio extraído
```

La relación entre fuente extraída y memoria viva es:

| Archivo | Naturaleza | ¿Quién lo consulta? | ¿Se modifica en partida? |
|---|---|---|---|
| `campaigns/<source_id>/*.md` | Estático: lo que dice el libro | Director (durante la sesión), Asistente (preparación) | No |
| `memory/<campaña>/*.md` | Dinámico: lo que ha pasado en la mesa | Director, Memory Keeper, Character Keeper | Sí |

### 3.6 Consulta durante la Partida (Director)

1. El Director sabe en qué capítulo está el grupo → carga
   `campaigns/<source_id>/capitulo_NN.md`.
2. Para un PNJ concreto → busca en `campaigns/<source_id>/npcs.md` y salta al
   capítulo vía enlace.
3. Para una localización → busca en `campaigns/<source_id>/locations.md` y
   salta al capítulo.
4. El boxed text se lee tal cual (bloque de cita), respetando el estilo
   narrativo configurado en el campaign compact.
5. Los stats de encuentros se cruzan con el bestiario de `rules/<game_id>/`
   para obtener valores mecánicos completos.

---

## 4. Extracción Masiva por Scripts

Cuando una categoría contiene más de 100 entradas individuales (conjuros —
ahora extraídos directamente al MCP, monstruos, objetos mágicos, PNJs) o el archivo raw supera las 5,000 líneas,
la extracción manual entrada por entrada es inviable. Se debe usar un
**script de automatización** (PowerShell o bash).

### 4.1 Procedimiento

1. **Leer el archivo `.txt` fuente completo**.
2. **Identificar cada entrada** mediante patrones de inicio y fin:
   - Conjuros: nombres seguidos de `Truco de` o `X de nivel Y`
   - Monstruos: nombres seguidos de tamaño y tipo
   - Objetos mágicos: nombres seguidos de rareza
   - PNJs de campaña: nombres seguidos de marcadores de sección o stats
   - Localizaciones: nombres seguidos de encabezados de área
3. **Extraer cada entrada** con sus campos completos, respetando el texto
   verbatim del `.txt`.
4. **Generar el `.md`** con el formato de la plantilla correspondiente
   (2.2 para reglas, 3.2 para campañas).
5. **Validar el archivo generado** antes de marcarlo como completo:
   - Ninguna línea > 5,000 caracteres (bug de parsing que fusiona entradas)
   - El conteo de entradas debe ser próximo al esperado
   - Muestrear al menos 5 entradas contra el `.txt` fuente

### 4.2 Patrón de Extracción Iterativa

Recomendado para archivos raw >5,000 líneas:

1. **Script inicial** → extrae la mayoría de entradas (~75-85%).
2. **Gap analysis** → comparar las entradas extraídas contra todos los nombres
   presentes en el raw para identificar las faltantes.
3. **Script de segunda pasada** → extraer las entradas faltantes.
4. **Concatenar** los resultados en el archivo `.md` definitivo.

### 4.3 Responsabilidad

El **Asistente** es responsable de crear, depurar y ejecutar el script.
Los subagentes (Rules Keeper, Memory Keeper) tienen limitaciones de contexto
para tareas muy extensas y delegan la automatización al Asistente. Una vez
generado el archivo, el agente especializado (Rules Keeper para reglas,
Memory Keeper para campañas) toma el relevo para la validación y auditoría.

---

## 5. Responsabilidades por Agente

### 5.1 Tabla de Extracción

| Agente | Reglas (SRD) | Campañas |
|---|---|---|
| **Asistente** | Crea y ejecuta scripts de extracción masiva. Genera `.md` de categorías. | Crea y ejecuta scripts de extracción. Genera capítulos e índices. |
| **Rules Keeper** | Extrae categorías pequeñas. Valida entradas contra `.txt`. Corrige en bucle. | No involucrado. |
| **Memory Keeper** | Audita extracciones contra `sistema_raw/`. Emite objeciones y visto bueno. | Audita extracciones contra `campaign_raw/`. Emite objeciones y visto bueno. Mantiene `campaigns/_index.md`. |
| **Director** | Consulta reglas durante la partida. | Consulta capítulos, PNJs, localizaciones durante la partida. Lee boxed text. |
| **Character Keeper** | Carga `personajes.md` para creación. Delega consultas al Rules Keeper. | No involucrado. |

### 5.2 Protocolo de Objeción (Memory Keeper)

Si el Memory Keeper encuentra un fallo en la auditoría:

1. **Emite objeción por escrito**: "OBJECIÓN: En `[archivo].md`, entrada
   [Nombre], falta [campo concreto]. El `.txt` fuente en `raw/` contiene [X]
   que no aparece en el `.md`. Debe incluirse antes del visto bueno."
2. **Cita la fuente**: Indica exactamente en qué `.txt` y en qué PAGINA
   aparece la información omitida/incorrecta.
3. **Espera** a que el agente extractor (Rules Keeper para reglas, Asistente
   para campañas) corrija el archivo.
4. **Re-verifica**: ¿Se añadió correctamente? ¿Los valores coinciden con el
   `.txt`? ¿La adición no introdujo contradicciones?
5. **Visto bueno**: "✅ [Categoría/Capítulo] auditado. VISTO BUENO SIN OBJECIONES."
6. **Escalación**: Si tras 3 iteraciones de corrección el fallo persiste,
   escala al Asistente con el historial de objeciones.

### 5.3 Delegación de Extracciones Masivas

Los subagentes (Rules Keeper, Memory Keeper) tienen limitaciones de contexto en
tareas muy extensas. Para extracciones de más de 100 entradas o archivos raw de
más de 5,000 líneas, el **Asistente** debe ejecutar scripts de extracción
directamente (sección 4). Los subagentes son efectivos para tareas acotadas:
corregir errores puntuales, validar muestras, o extraer categorías pequeñas.

