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
│  │  HTML/    │  │  WS     │  │  Server    │  │
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
│   ├── index.html          # Cliente completo (HTML+JS+CSS)
│   └── js/                 # Copia de los fuentes JS
│       ├── config.js       # Configuración y mapa
│       ├── client.js       # WebSocket y FPS
│       ├── input.js        # Manejo de teclas
│       ├── main.js         # Entry point
│       ├── renderer.js    # Raycasting + sprites
│       └── ui.js          # Menús, HUD, consola
├── src/server/             # Backend Python
│   ├── __init__.py
│   ├── server.py           # HTTP server + WebSocket handler
│   ├── game_logic.py      # IA enemigos, combate, movimiento
│   ├── game_state.py      # Estado del juego, entidades
│   └── physics.py         # Colisiones, línea de vista
├── tests/
│   ├── e2e/               # Tests E2E con Playwright
│   └── unit/              # Tests unitarios Python
├── docs/                  # Documentación
├── package.json           # Dependencias npm (Playwright)
├── requirements.txt       # Dependencias Python
└── start.sh              # Script para iniciar el servidor
```

---

## Módulos del Proyecto

### Servidor (Python)

| Módulo | Responsabilidad | Dependencias |
|--------|-----------------|---------------|
| `server.py` | HTTP + WebSocket, game loop 60 FPS, broadcast | game_logic, game_state |
| `game_logic.py` | Movimiento jugador, IA enemigos, combate, win/lose | game_state, physics |
| `game_state.py` | Entidades (Player, Enemy, Corpse), configuración, parsing mapa | nenhuma |
| `physics.py` | Colisiones paredes, línea de vista, raycasting | game_state |

### Cliente (JavaScript)

| Módulo | Responsabilidad | Dependencias |
|--------|-----------------|---------------|
| `main.js` | Inicialización, loop de render | todas |
| `client.js` | WebSocket, sincronización de estado | ui.js |
| `input.js` | Captura de teclas, envío al servidor | client.js |
| `renderer.js` | Raycasting, renderizado paredes/sprites | config.js |
| `ui.js` | Menús, HUD, consola debug | todas |
| `config.js` | Constantes, mapa del juego | nenhuma |

---

## Dependencias entre Módulos

### Servidor
```
server.py
    │
    ├── game_state.py (importa GameState, GameConfig)
    │       │
    │       └── (define Player, Enemy, Corpse, HitEffect, MAP_DATA)
    │
    └── game_logic.py (importa GameLogic)
            │
            └── physics.py (importa Physics)
```

### Cliente
```
main.js
    │
    ├── client.js
    │       │
    │       └── ui.js (updateUI, showScreen)
    │
    ├── input.js
    │       │
    │       └── client.js (ws.send)
    │
    ├── renderer.js
    │       │
    │       └── config.js (CONFIG, MAP_WIDTH, MAP_HEIGHT)
    │
    └── ui.js
            │
            ├── client.js (ws.send, gameState)
            ├── input.js (keys)
            └── config.js (CONFIG)
```

---

## Protocolo de Comunicación

### WebSocket (puerto 8001)

**Del cliente al servidor:**
```json
{ "type": "input", "keys": { "KeyW": true, "KeyA": false, ... } }
{ "type": "start" }
{ "type": "attack" }
{ "type": "resume" }
{ "type": "menu" }
{ "type": "console_command", "command": "god" }
{ "type": "console_command", "command": "speed", "value": 2 }
```

**Del servidor al cliente:**
```json
{
  "game_state": "playing",
  "player": { "x": 1.5, "y": 1.5, "angle": 0, "health": 100, "attack_cooldown": 0 },
  "enemies": [...],
  "corpses": [...],
  "kills": 0,
  "hit_effects": [...]
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

---

## Servidor HTTP (puerto 8000)

- Serve archivos estáticos desde `public/`
- Endpoint `/log` para logging del cliente

---

## Game Loop

1. **Input**: Cliente envía teclas presionadas via WebSocket
2. **Process**: Servidor actualiza lógica (60 FPS)
   - `GameLogic.update()` → `move_player()` → `update_enemies()` → `check_conditions()`
3. **State**: Servidor mantiene estado completo (`GameState`)
4. **Broadcast**: Servidor envía estado serializado a todos los clientes
5. **Render**: Cliente renderiza según estado recibido

---

## Estados de los Enemigos

| Estado | Comportamiento |
|--------|----------------|
| `patrol` | Movimiento aleatorio |
| `chase` | Persigue al jugador |
| `attack` | Ataca al jugador (daño) |
| `dying` | Animación de muerte |
| `dead` | Corpse permanece en mapa |

---

## Dependencias Externas

### Python
- `websockets` - WebSocket server
- `asyncio` - Async I/O (stdlib)

### JavaScript (Browser)
- HTML5 Canvas API
- WebSocket API
- requestAnimationFrame

### npm
- `playwright` - Tests E2E
