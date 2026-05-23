---
type: rules
game: dnd_5e
created: 2026-05-15
updated: 2026-05-23
tags: [rules, dnd_5e, magic, spell_system]
---

# Magia — SRD 5.2.1

Fuente: `SP_SRD_CC_v5.2.1.pdf`. Reglas del sistema de magia extraídas de `sistema_raw/06_conjuros.txt`. El catálogo de conjuros se consulta vía MCP (`conjuros_buscar_conjuro`, `conjuros_listar_conjuros`).

---

## Reglas generales de lanzamiento de conjuros

### Lanzar conjuros con armadura
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 114
- **Versión**: SRD 5.2.1 (2024)
- **Tags**: `#magia #lanzamiento #armadura`
- **Regla**: Debes tener entrenamiento con la armadura que llevas para lanzar conjuros vistiéndola. De lo contrario, la armadura será un lastre excesivo para lanzar conjuros.

### Obtener conjuros
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 114
- **Tags**: `#magia #conjuros #aprendizaje`
- **Regla**: Para poder lanzar un conjuro, debes prepararlo en tu mente o tener acceso a él a través de un objeto mágico, como un pergamino de conjuro. Tus rasgos indican a qué conjuros tienes acceso (de tenerlo), si tienes ciertos conjuros preparados siempre y si puedes cambiar la lista de conjuros que tengas preparados.

### Preparar conjuros
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 114
- **Tags**: `#magia #preparacion`
- **Regla**: Si tienes que preparar una lista de conjuros de nivel 1 o superiores, tu rasgo de lanzamiento de conjuros indica cuándo puedes cambiar la lista y cuántos conjuros puedes cambiar, como se resume en la tabla "Preparación de conjuros según clase".

**Tabla — Preparación de conjuros según clase:**

| Clase | ¿Cuándo cambia? | Cantidad de conjuros |
|---|---|---|
| Bardo | Al subir de nivel | Uno |
| Brujo | Al subir de nivel | Uno |
| Clérigo | Al finalizar un descanso largo | Cualquiera |
| Druida | Al finalizar un descanso largo | Cualquiera |
| Explorador | Al finalizar un descanso largo | Uno |
| Hechicero | Al subir de nivel | Uno |
| Mago | Al finalizar un descanso largo | Cualquiera |
| Paladín | Al finalizar un descanso largo | Uno |

La mayoría de monstruos que lanzan conjuros no cambian su lista de conjuros preparados, pero cada GM puede modificarla libremente.

### Conjuros siempre preparados
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 114
- **Tags**: `#magia #preparacion`
- **Regla**: Es posible que algunos rasgos te otorguen conjuros que siempre tienes preparados. Si también tienes una lista de conjuros preparados que puedes modificar, los conjuros que tengas preparados siempre no contarán para el total de esa lista.

### Nivel del conjuro
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 114
- **Tags**: `#magia #nivel`
- **Regla**: Todos los conjuros tienen un nivel que va de 0 a 9 y que se indica en su descripción. Este nivel indica lo poderoso que es el conjuro. Además, existen los trucos, unos conjuros sencillos que se pueden lanzar casi de forma rutinaria y que son de nivel 0. Las reglas para cada clase capaz de lanzar conjuros indican cuándo obtienen acceso a conjuros de ciertos niveles los miembros de esa clase.

### Espacios de conjuro
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 114
- **Tags**: `#magia #espacios`
- **Regla**: El lanzamiento de conjuros es extenuante, así que un lanzador solo puede lanzar un número limitado de conjuros de nivel 1 o superior antes de tener que descansar. Los espacios de conjuro son la forma principal en la que se representa el potencial mágico de un lanzador de conjuros. Cuando lanzas un conjuro, gastas un espacio del mismo nivel del conjuro o superior y, de esta forma, "llenas" dicho espacio con el conjuro. Un conjuro de nivel 1 cabe en un espacio de cualquier tamaño, pero uno de nivel 2 necesita un espacio de nivel 2 como mínimo. Los espacios de conjuro utilizados se recuperan tras finalizar un descanso largo.

### Lanzar conjuros sin espacios
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #trucos #rituales`
- **Regla**: Hay varias formas de lanzar un conjuro sin gastar un espacio de conjuro:
  - **Trucos**: Los trucos se lanzan sin emplear espacios de conjuro.
  - **Rituales**: Algunos conjuros están marcados como "ritual" en el apartado del tiempo de lanzamiento. Se puede lanzar dichos conjuros utilizando las reglas habituales o de forma ritual. Lanzar un conjuro de forma ritual requiere 10 minutos más del tiempo normal, pero no gasta ningún espacio de conjuro. Para lanzar un conjuro de forma ritual, el lanzador debe tenerlo preparado.
  - **Capacidades especiales**: Algunos personajes y monstruos tienen capacidades especiales que les permiten lanzar conjuros específicos sin ningún espacio de conjuro.
  - **Objetos mágicos**: Los pergaminos de conjuro y otros objetos mágicos contienen conjuros que se pueden lanzar sin ningún espacio de conjuro.

### Usar espacios de conjuro de niveles superiores
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #niveles-superiores`
- **Regla**: Si un lanzador de conjuros utiliza un espacio de mayor nivel que el conjuro que lanza, dicho conjuro pasa a ser del nivel del espacio a efectos de ese lanzamiento. Algunos conjuros se vuelven más poderosos al lanzarlos a un nivel superior, como se explica en sus descripciones.

### Escuela mágica
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #escuelas`
- **Regla**: Cada conjuro pertenece a una escuela mágica, que se muestran en la tabla "Escuelas mágicas". Estas categorías ayudan a describir conjuros, pero no tienen ninguna regla asociada. No obstante, otras reglas hacen referencia a estas escuelas.

**Tabla — Escuelas mágicas:**

| Escuela | Efectos típicos |
|---|---|
| Abjuración | Impide o deshace efectos dañinos |
| Adivinación | Revela información |
| Conjuración | Transporta criaturas u objetos |
| Encantamiento | Influye en las mentes |
| Evocación | Canaliza la energía para crear efectos, a menudo destructivos |
| Ilusionismo | Engaña a la mente o los sentidos |
| Nigromancia | Manipula la vida y la muerte |
| Transmutación | Transforma criaturas u objetos |

### Listas de conjuros de clases
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #clases`
- **Regla**: Si un conjuro forma parte de la lista de una clase, el nombre de la clase aparecerá entre paréntesis tras la escuela mágica. Algunos rasgos otorgan conjuros a la lista de un personaje incluso si no tiene la clase indicada entre paréntesis.

### Tiempo de lanzamiento
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #tiempo-lanzamiento`
- **Regla**: La mayoría de los conjuros precisan de una acción de magia para lanzarlos, pero algunos requieren una acción adicional, una reacción, 1 minuto o más tiempo. En el apartado del tiempo de lanzamiento se indica qué será necesario.

### Un conjuro por cada espacio de conjuro y turno
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #reglas`
- **Regla**: Durante un turno, solo puedes gastar un espacio de conjuro para lanzar un conjuro. Esto significa que no puedes, por ejemplo, lanzar un conjuro gastando un espacio como acción de magia y otro como acción adicional en el mismo turno.

### Desencadenantes de reacciones y acciones adicionales
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #reaccion #accion-adicional`
- **Regla**: Si el tiempo de lanzamiento de un conjuro es una reacción, se lanza en respuesta a un suceso definido en el apartado del tiempo de lanzamiento del conjuro. Algunos conjuros que tienen un tiempo de lanzamiento de una acción adicional también se lanzan en respuesta a un suceso definido en el conjuro.

### Tiempos de lanzamiento más largos
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #concentracion #rituales`
- **Regla**: Ciertos conjuros (incluyendo los que se lanzan como rituales) requieren más tiempo para lanzarlos, ya sean varios minutos o incluso horas. Mientras lanzas un conjuro que tiene un tiempo de lanzamiento de 1 minuto o más, deberás realizar la acción de magia en cada uno de tus turnos y mantener la concentración mientras lo haces. Si pierdes la concentración, el conjuro fallará, pero no gastarás un espacio de conjuro. Para volver a lanzar el conjuro, deberás empezar de nuevo.

### Alcance
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #alcance`
- **Regla**: El alcance de un conjuro indica a qué distancia de su lanzador se puede originar su efecto. Normalmente, el alcance de un conjuro se presenta en una de estas formas:
  - **Distancia**: El alcance se expresa en metros.
  - **Toque**: El efecto del conjuro se origina en algo que el lanzador debe tocar dentro de su alcance, como se define en el conjuro.
  - **Lanzador**: El conjuro se lanza sobre el usuario o emana de él, según se indique en el conjuro.
  Si un conjuro tiene efectos desplazables, no se verán restringidos por su alcance, salvo que la descripción indique lo contrario.

### Identificar un conjuro activo
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116
- **Tags**: `#magia #identificar`
- **Regla**: Si aún está activo, puedes intentar identificar un conjuro no instantáneo por sus efectos observables. Para ello, debes llevar a cabo una acción de estudiar y superar una prueba de Inteligencia (Conocimiento arcano) con CD 15.

### Componentes — Verbal (V)
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116
- **Tags**: `#magia #componentes #verbal`
- **Regla**: Un componente verbal consiste en un canto esotérico que carece de sentido para quienes no practican la magia. Las palabras deben pronunciarse con voz normal. Una criatura amordazada o en una zona de silencio mágico no podrá lanzar conjuros con componente verbal.

### Componentes — Somático (S)
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116
- **Tags**: `#magia #componentes #somático`
- **Regla**: Un componente somático es la ejecución de gestos enérgicos o intrincados. Un lanzador de conjuros deberá tener al menos una mano libre para hacer estos movimientos.

### Componentes — Material (M)
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116
- **Tags**: `#magia #componentes #material`
- **Regla**: Un componente material es un objeto concreto que se emplea para lanzar un conjuro, como se indica entre paréntesis en el apartado de componentes. El conjuro no gasta estos materiales, a menos que su descripción indique algo distinto. El lanzador deberá tener una mano libre para poder acceder a ellos, aunque puede ser la misma que use para ejecutar los componentes somáticos, si los hay. Si un conjuro no gasta los materiales y no se especifica un coste para ellos, el lanzador puede usar un saquito de componentes en vez de portar los materiales indicados en el conjuro o sustituirlos por un canalizador mágico si posee un rasgo que le permita reemplazarlos.

### Duración
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116
- **Tags**: `#magia #duracion`
- **Regla**: La duración de un conjuro es el tiempo que este permanece activo después de lanzarlo. Normalmente, la duración de un conjuro se presenta en una de estas formas:
  - **Concentración**: Si la duración requiere concentración, sigue las reglas correspondientes del glosario de reglas.
  - **Instantáneo**: La magia del conjuro tendrá efecto solo un instante y luego desaparecerá.
  - **Periodo de tiempo**: Especifica cuánto dura el conjuro en asaltos, minutos, horas o similares. Mientras un conjuro que tú hayas lanzado siga activo dentro de su periodo de tiempo, puedes ponerle fin (no requiere acción) si no tienes el estado de incapacitado.

### Efectos
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116
- **Tags**: `#magia #efectos`
- **Regla**: Los efectos de un conjuro se describen tras el apartado de la duración. Estos detalles indican con exactitud lo que hace el conjuro, que ignora las leyes físicas normales. Cualquier otro resultado más allá de sus efectos queda a discreción de cada GM. Sean cuales sean los efectos, suelen tener que ver con objetivos, tiradas de salvación, tiradas de ataque o las tres cosas a la vez.

### Objetivos
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 116-117
- **Tags**: `#magia #objetivos`
- **Regla**: Lo más normal es que un conjuro obligue a su lanzador a elegir uno o más objetivos. La descripción de un conjuro indica si hace objetivo a criaturas, objetos u otra cosa.
  - **Un camino despejado hasta el objetivo**: Para poder elegir un objetivo para un conjuro, el lanzador deberá tener una ruta clara hasta él, por lo que no podrá estar tras cobertura completa.
  - **Elegirte como objetivo**: Si un conjuro tiene como objetivo a una criatura de tu elección, podrás designarte a ti como tal, siempre y cuando no se indique que la criatura debe ser hostil o, explícitamente, que tú no puedes ser el objetivo.
  - **Áreas de efecto**: Algunos conjuros abarcan una zona denominada "área de efecto", que se define en el glosario de reglas. Dicha área determina los objetivos del conjuro. Normalmente será una de las siguientes formas: cilindro, cono, cubo, emanación, esfera o línea.
  - **Conciencia de ser objetivo**: Salvo que un conjuro tenga un efecto perceptible, el objetivo no sabrá que se está lanzando un conjuro sobre él.
  - **Objetivos no válidos**: Si lanzas un conjuro sobre alguien o algo que no pueda verse afectado por él, no le pasará nada. Sin embargo, si has usado un espacio de conjuro para lanzarlo, ese espacio se gastará igualmente. Si un conjuro normalmente no tiene efecto sobre un objetivo que supere una tirada de salvación, un objetivo no válido parecerá haber superado su tirada de salvación, aunque no haya hecho una.

### Tiradas de salvación
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 117
- **Tags**: `#magia #salvacion`
- **Regla**: Muchos conjuros especifican que un objetivo hace una tirada de salvación para evitar parte de sus efectos o todos ellos. Cada conjuro indica la característica que el objetivo debe usar para la tirada y qué ocurre en caso de éxito o fallo. **CD de salvación de conjuros** = 8 + tu modificador por aptitud mágica + tu bonificador por competencia.

### Tiradas de ataque
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 117
- **Tags**: `#magia #ataque`
- **Regla**: Algunos conjuros necesitan que el lanzador haga una tirada de ataque para determinar si aciertan al objetivo. **Modificador de ataque de conjuros** = tu modificador por aptitud mágica + tu bonificador por competencia.

### Combinar efectos de conjuros
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 117
- **Tags**: `#magia #efectos`
- **Regla**: Los efectos de varios conjuros se suman si sus duraciones se solapan. En cambio, los efectos del mismo conjuro lanzado varias veces no se combinan. En vez de eso, se aplica el efecto más potente (como el bonificador más alto) de los lanzamientos mientras se solapen sus duraciones. Si los lanzamientos son igual de potentes y sus duraciones se solapan, se aplica el efecto más reciente.

### Concentración
- **Fuente**: `sistema_raw/07_glosario_reglas.txt`, PÁGINA 194
- **Tags**: `#magia #concentracion`
- **Regla**: Algunos conjuros y otros efectos requieren concentración para mantenerse activos. Si un efecto requiere concentración, se indica en su duración. Condiciones: (1) solo puedes concentrarte en un efecto a la vez, (2) si lanzas otro conjuro que requiera concentración, pierdes el anterior, (3) si recibes daño mientras te concentras, haz una salvación de Constitución CD 10 o la mitad del daño recibido (la que sea mayor) o pierdes la concentración, (4) quedar incapacitado o muerto rompe la concentración, (5) el lanzador puede terminar la concentración en cualquier momento sin acción.

### Conjuros con ritual
- **Fuente**: `sistema_raw/06_conjuros.txt`, PÁGINA 115
- **Tags**: `#magia #ritual`
- **Regla**: Un conjuro con la etiqueta Ritual en su tiempo de lanzamiento puede lanzarse como ritual. Esto añade 10 minutos al tiempo de lanzamiento pero no gasta un espacio de conjuro. Para lanzarlo como ritual, el conjuro debe estar preparado o en el libro de conjuros (magos).

