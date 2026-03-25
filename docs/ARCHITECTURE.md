# Arquitectura de WebDoom

## Visión General

WebDoom es un juego FPS estilo DOOM con arquitectura cliente-servidor:
- **Cliente**: HTML5 Canvas + Vanilla JavaScript
- **Servidor**: Python 3 + WebSockets + asyncio

---

## Diagrama de Arquitectura

```
┌─────────────────┐         ┌─────────────────┐
│   Cliente       │         │    Servidor     │
│   (Browser)     │         │    (Python)     │
│                 │         │                 │
│  ┌───────────┐  │         │  ┌───────────┐  │
│  │  HTML/    │  │  WS     │  │  Server   │  │
│  │  Canvas   │◄─┼─────────┼─►│  (HTTP+   │  │
│  └───────────┘  │         │  │   WS)     │  │
│                 │         │  └─────┬─────┘  │
│  ┌───────────┐  │         │        │        │
│  │  UI       │  │         │  ┌─────┴─────┐  │
│  │ (menús,   │  │         │  │ GameLogic │  │
│  │  HUD)     │  │         │  └─────┬─────┘  │
│  └───────────┘  │         │        │        │
│                 │         │  ┌─────┴─────┐  │
│  ┌───────────┐  │         │  │GameState   │  │
│  │ Rendering │  │         │  │+Physics    │  │
│  │(Raycasting│  │         │  └───────────┘  │
│  └───────────┘  │         │                 │
└─────────────────┘         └─────────────────┘
```

---

## Estructura de Archivos

```
WebDoom/
├── public/                  # Frontend estático
│   └── index.html          # Cliente completo (HTML+JS+CSS)
├── src/server/              # Backend Python
│   ├── __init__.py
│   ├── server.py           # HTTP server + WebSocket handler
│   ├── game_logic.py      # IA enemigos, combate, movimiento
│   ├── game_state.py      # Estado del juego, entidades
│   └── physics.py         # Colisiones, línea de vista
├── tests/
│   └── e2e/               # Tests E2E con Playwright
│       └── game.test.js
├── docs/                   # Documentación
├── package.json            # Dependencias npm
├── requirements.txt       # Dependencias Python
└── start.sh               # Script para iniciar el servidor
```

---

## Protocolo de Comunicación

### WebSocket (puerto 8001)

**Del cliente al servidor:**
```json
{ "type": "input", "keys": { "w": true, "a": false, ... } }
{ "type": "start" }
{ "type": "attack" }
{ "type": "resume" }
{ "type": "menu" }
{ "type": "console_command", "command": "god" }
```

**Del servidor al cliente:**
```json
{
  "type": "state",
  "game_state": "playing",
  "player": { "x": 1.5, "y": 1.5, "angle": 0, "health": 100 },
  "enemies": [...],
  "corpses": [...],
  "kills": 0
}
```

---

## Estados del Juego

| Estado | Descripción |
|--------|-------------|
| `menu` | Pantalla inicial |
| `playing` | Partida en curso |
| `victory` | Victoria (todos enemigos muertos) |
| `defeat` | Derrota (jugador muerto) |
| `paused` | Juego en pausa |

---

## Servidor HTTP (puerto 8000)

- Serve archivos estáticos desde `public/`
- Endpoint `/log` para logging del cliente

---

## Game Loop

1. **Input**: Cliente envía teclas presionadas
2. **Process**: Servidor actualiza lógica (60 FPS)
3. **State**: Servidor mantiene estado completo
4. **Broadcast**: Servidor envía estado a todos los clientes
5. **Render**: Cliente renderiza según estado recibido