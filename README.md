# OpenMaster

![Estado: Alpha](https://img.shields.io/badge/estado-Alpha-orange)

Sistema de agentes de IA para dirigir partidas de rol usando [OpenCode](https://opencode.ai). Memoria persistente en markdown con frontmatter YAML, diseñado para ser agnóstico al sistema de juego.

> **Alpha**: funcional pero en desarrollo activo. Pueden ocurrir cambios, bugs o ajustes de arquitectura.

---

## Qué es OpenMaster

OpenMaster es un conjunto de agentes de IA orquestados que trabajan juntos para asistir o dirigir completamente una partida de rol. En lugar de un solo prompt monolítico, OpenMaster divide la responsabilidad entre 6 agentes especializados:

- **Director** — Narra, interpreta PNJs y arbitra reglas
- **Asistente** — Ayudante del Director, documenta y consulta
- **Rules Keeper** — Consulta y aplica el sistema de reglas
- **Memory Keeper** — Gestiona la memoria persistente de campaña
- **Character Keeper** — Gestiona fichas y estado de personajes
- **Combat Keeper** — Gestiona y narra combates

Cada agente tiene acceso de lectura a toda la memoria y responsabilidades de escritura específicas, siguiendo el protocolo definido en [`AGENTS.MD`](AGENTS.MD).

---

## Cómo usar OpenMaster

1. Instala [OpenCode](https://opencode.ai) (CLI o extensión de VS Code)
2. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd OpenMaster
   ```
3. Abre la carpeta con OpenCode:
   ```bash
   opencode .
   ```
   O desde VS Code con la extensión OpenCode instalada: `Archivo > Abrir carpeta` y usa el comando `OpenCode: Start Agent`.
4. El agente `director` está configurado por defecto en `.opencode/opencode.json`
5. ¡Empieza a jugar! El Director te guiará en la creación de campaña y personajes.

---

## Modelos gratuitos recomendados

OpenMaster funciona con cualquier modelo compatible con OpenCode. Estos son los proveedores con modelos de uso gratuito o capa gratuita con los que mejor se comporta:

| Proveedor | Modelo recomendado | Notas |
|---|---|---|
| [OpenCode Zen](https://opencode.ai) | **DeepSeek V4 Flash** | Modelo con el que se ha probado el proyecto. Rápido, de alta calidad y disponible en OpenCode Zen. |
| [OpenRouter](https://openrouter.ai) | Varios modelos open-source | Cuota gratuita diaria. Amplia variedad de modelos. |
| [Groq](https://groq.com) | Llama 3, Mixtral | Inferencia ultrarrápida. Capa gratuita muy generosa. |
| [GitHub Models](https://github.com/marketplace/models) | GPT-4o-mini, DeepSeek-R1 | Cuota gratuita con cuenta de GitHub. |
| [Google AI Studio](https://aistudio.google.com) | Gemini 2.0 Flash | API gratuita con límites generosos. |

Los modelos se configuran en OpenCode según el proveedor (variables de entorno, API key en `opencode.json`, o mediante el cliente oficial).

---

## Cómo reportar errores

Si durante el uso la IA detecta o corrige un error (inconsistencias en la memoria, reglas mal extraídas, bugs de parsing, etc.), debe generar automáticamente un informe en la raíz del proyecto con el formato `bug_report_YYYY-MM-DD.md` que incluya:

- Descripción del error
- Causas identificadas
- Solución aplicada (o propuesta)

Para errores generales, dudas o sugerencias, abre un issue en el repositorio del proyecto.

---

## Arquitectura (para contribuidores)

OpenMaster sigue una arquitectura de agentes con memoria estructurada en markdown. La documentación completa está en [`AGENTS.MD`](AGENTS.MD), que cubre:

- Roles y responsabilidades de cada agente
- Estructura de directorios y convenciones de archivo
- Esquemas de frontmatter YAML para cada tipo de memoria
- Protocolos de ciclo de vida (inicio de campaña, sesión, cierre)
- Protocolo de extracción de reglas desde SRDs
- Protocolo de creación de personajes
- Formato de respuesta narrativa y mecánica

La configuración del proyecto se encuentra en `.opencode/opencode.json` y los agentes en `.opencode/agents/`.

---

## Licencia

Ver el archivo [`LICENSE`](LICENSE).
