---
type: rules
game: dnd_5e
created: 2026-05-15
updated: 2026-05-15
tags: [rules, dnd_5e, format]
---

# Formato Mecánico — D&D 5e

Este archivo define la notación compacta para el **bloque mecánico** de las respuestas en partida. El agente debe usar este formato para todas las acciones resueltas.

---

## Ataque con éxito

```
[ESPADA LARGA] 1d20(13) + 5 = 18 ≥ CA 15 → ✅ ACIERTO
  Daño: 1d8(5) + 3 = 8 cortante 🩸
```

## Ataque fallido

```
[ARCO CORTO] 1d20(4) + 6 = 10 < CA 14 → ❌ FALLO
```

## Crítico

```
[DAGA] 🎯 1d20(20) + 6 = 26 ≥ CA 12 → 🔥 CRÍTICO
  Daño: 2d4(3,4) + 4 = 11 perforante 🩸
```

## Pifia

```
[HACHA DE MANO] 💀 1d20(1) + 5 = 6 → PIFIA
```

## Ataque de oportunidad

```
[ESPADA CORTA] ⚡ OPORTUNIDAD: 1d20(11) + 6 = 17 ≥ CA 14 → ✅ ACIERTO
  Daño: 1d6(4) + 4 = 8 perforante 🩸
```

## Ataque con ventaja

```
[ARCO LARGO] VENTAJA 2d20(7,15) → 15 + 7 = 22 ≥ CA 13 → ✅ ACIERTO
  Daño: 1d8(6) + 3 = 9 perforante 🩸
```

## Ataque con desventaja

```
[LANZA (arrojadiza)] DESVENTAJA 2d20(17,3) → 3 + 2 = 5 < CA 15 → ❌ FALLO
```

## Tirada de salvación superada

```
[SALV. DESTREZA vs BOLA DE FUEGO] 1d20(14) + 2 = 16 ≥ CD 15 → ✅ SALVADA
  Daño: 8d6(28) / 2 = 14 fuego 🔥
```

## Tirada de salvación fallida

```
[SALV. CONSTITUCIÓN vs VENENO] 1d20(3) + 1 = 4 < CD 12 → ❌ FALLIDA
  Estado: envenenado ☠️
```

## Salvación contra muerte

```
[SALV. CONTRA MUERTE] 1d20(17) = 17 ≥ 10 → ✅ ÉXITO (1/3)
```

## Prueba de habilidad con éxito

```
[ATLETISMO (FUE) para escalar] 1d20(15) + 5 = 20 ≥ CD 15 → ✅ ÉXITO
```

## Prueba de habilidad fallida

```
[SIGILO (DES) para esconderse] 1d20(4) + 7 = 11 < CD 14 → ❌ FALLO
```

## Lanzamiento de conjuro con ataque

```
[RAyo DE FUEGO] 1d20(9) + 5 = 14 ≥ CA 13 → ✅ ACIERTO
  Daño: 2d10(8,6) = 14 fuego 🔥
```

## Lanzamiento de conjuro con salvación

```
[DORMIR] ✨ 5d8(26) PG afectados → Criatura A (PG: 12) ☠️ dormida
```

## Curación

```
[CURAR HERIDAS] 💚 Recuperas 1d8(5) + 3 = 8 PG
  PG: 12/20
```

## Resistencia

```
[GARRAS] 1d20(14) + 5 = 19 ≥ CA 15 → ✅ ACIERTO
  Daño: 2d6(7) + 3 = 10 cortante 🩸 → RESISTENCIA 🛡️ → 5 cortante 🩸
```

## Inmunidad

```
[ALIENTO DE FUEGO] SALV. DES: CD 13 🔥
  Criatura: inmune al fuego 🛡️ → 0 daño
```

## Cobertura

```
[FLECHA] 1d20(12) + 5 = 17 vs CA 15 + 2 (cobertura media) = 17 → ✅ ACIERTO
  Daño: 1d8(4) + 3 = 7 perforante 🩸
```

## Movimiento

```
📍 Movimiento: 9 m hacia el altar. Posición: E5 → E8.
```

---

## Estructura del bloque mecánico

```
[ORIGEN] [MODIFICADOR_ESPECIAL] DADOS(resultados) + MOD = TOTAL ≥/< CD → EMOJI RESULTADO
  [Efecto]: [detalle] EMOJI_EFECTO
```

### Reglas de formato
1. `[ORIGEN]` — arma, conjuro, habilidad o tipo de tirada (entre corchetes, mayúsculas)
2. `[MODIFICADOR_ESPECIAL]` — si aplica: VENTAJA, DESVENTAJA, ⚡ OPORTUNIDAD
3. Dados: `XdY(resultados)` donde resultados son los valores obtenidos
4. Símbolos: `≥` éxito, `<` fallo, separar con `→`
5. Efecto en línea sangrada con 2 espacios
6. PG actuales: mostrar al final tras cambios de curación/daño
