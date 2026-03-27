# WebDoom - Architecture

## Overview

WebDoom is a DOOM-style FPS game with client-server architecture:
- **Client**: HTML5 Canvas + Vanilla JavaScript
- **Server**: Python 3 + WebSockets + asyncio

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVER (Python)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐      ┌─────────────────────┐                      │
│  │   GameEngine        │◄─────│   GameState         │                      │
│  │   (Facade)          │      │                     │                      │
│  │                     │      │ - player            │                      │
│  │ - player_system     │      │ - enemies[]         │                      │
│  │ - enemy_system      │      │ - corpses[]         │                      │
│  │ - combat_system    │      │ - map               │                      │
│  │ - weapon_system    │      │ - game_mode         │                      │
│  └──────────┬──────────┘      └─────────────────────┘                      │
│             │                                                              │
│  ┌──────────┴─────────────────────────────────────────────────────┐        │
│  │                     SYSTEMS (ISystem)                           │        │
│  ├─────────────────┬─────────────────┬─────────────────┬────────────┤        │
│  │ PlayerMovement  │ EnemyAI         │ CombatSystem   │ Physics    │        │
│  │ System         │ System          │ + Weapons      │ Engine     │        │
│  └─────────────────┴─────────────────┴─────────────────┴────────────┘        │
│                                                                             │
│  ┌─────────────────────┐      ┌─────────────────────┐                      │
│  │   EventSystem       │      │   EntityFactory     │                      │
│  │   (Dispatcher)      │      │   (Factory)         │                      │
│  │                     │      │                     │                      │
│  │ - subscribe        │      │ + create_player()  │                      │
│  │ - emit             │      │ + create_enemy()   │                      │
│  │ - process_queue    │      │ + create_weapon()  │                      │
│  └─────────────────────┘      └─────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT (JavaScript)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Game (Facade)                                   │   │
│  │  - networkManager: NetworkManager                                   │   │
│  │  - inputManager: InputManager                                       │   │
│  │  - state: GameState (Observable)                                     │   │
│  │  - renderer: WallRenderer                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                    │                    │                    │                │
│  ┌────────────────┴────────┐  ┌────────┴────────┐  ┌───────┴────────┐        │
│  │     WallRenderer         │  │   InputManager   │  │ NetworkManager  │        │
│  │                         │  │                  │  │                  │        │
│  │ - Raycaster             │  │ - Keyboard       │  │ - WebSocket      │        │
│  │ - Sprite Rendering      │  │ - Mouse         │  │ - Protocol       │        │
│  │ - Ceiling/Floor         │  │ - Touch         │  │ - Reconnector    │        │
│  └─────────────────────────┘  └────────────────┘  └────────────────┘        │
│                                                                             │
│  ┌─────────────────────────┐  ┌──────────────────────────────────────┐    │
│  │      UIManager          │  │         GameState (Observable)       │    │
│  │                         │  │                                      │    │
│  │ - ScreenManager         │  │  - player: Player                   │    │
│  │ - HUDManager            │  │  - enemies: Enemy[]                  │    │
│  │ - ConsoleManager       │  │  - observers: Observer[]            │    │
│  └─────────────────────────┘  └──────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          SHARED                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐   │
│  │   constants.py      │  │   constants.js     │  │  protocol.json  │   │
│  │   (Server)          │  │   (Client)          │  │  (Schema)       │   │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────┘   │
│                                                                             │
│  ┌─────────────────────┐                                                  │
│  │   map-data.json    │                                                  │
│  │   (Single source)   │                                                  │
│  └─────────────────────┘                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
WebDoom/
├── public/                          # Frontend static files
│   ├── index.html                  # HTML + CSS
│   └── js/
│       ├── main.js                 # Entry point
│       ├── game.js                 # Game facade
│       ├── config.js               # Configuration
│       ├── client.js               # WebSocket client
│       ├── input.js                # Input handling
│       ├── renderer.js             # Main renderer
│       ├── ui.js                   # UI management
│       ├── core/
│       │   ├── game-state.js       # Observable state
│       │   └── observable.js        # Observer pattern
│       ├── systems/
│       │   ├── network-manager.js  # WebSocket handling
│       │   └── input-manager.js    # Unified input
│       └── rendering/
│           └── raycaster.js         # Raycasting engine
│
├── src/server/                     # Backend Python
│   ├── __init__.py
│   ├── server.py                   # HTTP + WebSocket server
│   ├── game_engine.py              # GameEngine facade
│   ├── game_logic.py              # Original logic (compat)
│   ├── game_state.py              # Entities, state
│   ├── physics.py                 # Collisions, raycasting
│   ├── core/
│   │   ├── interfaces.py          # Abstract interfaces
│   │   └── event_system.py        # Event dispatcher
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── base.py                 # ISystem base
│   │   ├── player_system.py        # Player movement
│   │   ├── enemy_ai_system.py      # Enemy AI
│   │   ├── combat_system.py        # Combat
│   │   └── weapon_system.py        # Weapons + Items
│   ├── networking/
│   │   └── protocol.py             # Delta compression
│   └── factory/
│       └── entity_factory.py        # Entity creation
│
├── shared/                         # Shared code
│   ├── constants.py               # Server constants
│   ├── constants.js               # Client constants
│   ├── map-data.json              # Map data (single source)
│   └── protocol.json              # Protocol schema
│
├── tests/
│   ├── unit/                      # Unit tests (pytest)
│   │   ├── test_physics.py
│   │   ├── test_ai.py
│   │   ├── test_combat.py
│   │   └── test_systems.py
│   └── e2e/                       # E2E tests (Playwright)
│       └── game.test.js
│
├── docs/                          # Documentation
├── package.json                   # npm dependencies
├── requirements.txt               # Python dependencies
├── start.sh                      # Start script
└── .venv/                        # Virtual environment
```

---

## Module Responsibilities

### Server (Python)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `server.py` | HTTP + WebSocket, game loop 60 FPS, broadcast | game_logic, game_state |
| `game_engine.py` | System orchestration (Facade) | systems/*, physics |
| `game_logic.py` | Original logic (backward compat) | game_state, physics |
| `game_state.py` | Entities, state, map parsing | none |
| `physics.py` | Collisions, line of sight, raycasting | game_state |
| `core/event_system.py` | Event dispatcher | none |
| `systems/player_system.py` | Player movement | physics |
| `systems/enemy_ai_system.py` | Enemy AI behaviors | physics |
| `systems/combat_system.py` | Combat mechanics | none |
| `systems/weapon_system.py` | Weapons + Items | event_system |
| `networking/protocol.py` | Delta compression | none |
| `factory/entity_factory.py` | Entity creation | event_system |

### Client (JavaScript)

| Module | Responsibility |
|--------|----------------|
| `main.js` | Initialization, render loop |
| `game.js` | Game facade, state management |
| `client.js` | WebSocket, state sync |
| `input.js` | Keyboard input capture |
| `renderer.js` | Raycasting, sprites |
| `ui.js` | Menus, HUD, console |
| `config.js` | Constants, map |
| `core/observable.js` | Observer pattern |
| `core/game-state.js` | Observable state |
| `systems/network-manager.js` | WebSocket + reconnection |
| `systems/input-manager.js` | Unified input (keyboard, mouse, touch) |
| `rendering/raycaster.js` | Raycasting engine |

---

## Design Patterns

| Pattern | Implementation |
|---------|---------------|
| **Facade** | `GameEngine` (server), `Game` (client) |
| **Observer** | `Observable` / `GameState` notifies observers |
| **Factory** | `EntityFactory` creates all entities |
| **Strategy** | Interchangeable AI behaviors |
| **Command** | Network messages as commands |
| **ECS-light** | Systems operate on entity collections |
| **State** | Game state machine |

---

## Communication Protocol

### WebSocket (port 8001)

**Client → Server:**
```json
{ "type": "input", "keys": { "KeyW": true, "KeyA": false } }
{ "type": "start" }
{ "type": "attack" }
{ "type": "resume" }
{ "type": "menu" }
{ "type": "console_command", "command": "god" }
{ "type": "console_command", "command": "speed", "value": 2 }
```

**Server → Client (Full State):**
```json
{
  "type": "state",
  "mode": "full",
  "data": {
    "game_state": "playing",
    "player": { "x": 1.5, "y": 1.5, "angle": 0, "health": 100 },
    "enemies": [...],
    "corpses": [...],
    "kills": 0
  }
}
```

**Server → Client (Delta):**
```json
{
  "type": "state",
  "mode": "delta",
  "data": {
    "mode": "delta",
    "changes": { "player.health": 90 },
    "removed": ["enemy:e3"]
  }
}
```

---

## Game States

| State | Description |
|-------|-------------|
| `menu` | Initial screen |
| `playing` | Game in progress |
| `victory` | All enemies killed |
| `defeat` | Player dead |
| `pause` | Game paused |

---

## Enemy States

| State | Behavior |
|-------|----------|
| `patrol` | Random movement |
| `chase` | Pursues player |
| `attack` | Attacks player (damage) |
| `dying` | Death animation |
| `dead` | Corpse remains on map |

---

## Weapons

| Weapon | Type | Damage | Range | Cooldown |
|--------|------|--------|-------|----------|
| Fists | Melee | 10 | 1.5 | 0.5s |
| Chainsaw | Melee | 25 | 1.5 | 0.2s |
| Shotgun | Projectile | 10/pellet | 8.0 | 1.0s |
| Chaingun | Projectile | 8 | 15.0 | 0.1s |

---

## Event System

```python
from core.event_system import EventDispatcher, EventType, GameEvent

dispatcher = EventDispatcher()

# Subscribe to events
dispatcher.subscribe(EventType.ENEMY_DEATH, on_enemy_death)

# Emit events
dispatcher.emit(GameEvent(
    type=EventType.PLAYER_ATTACK,
    data={"target": enemy}
))

# Process queue
dispatcher.process_queue()
```

**Event Types:**
- `PLAYER_MOVE`, `PLAYER_ATTACK`, `PLAYER_DAMAGED`, `PLAYER_DEATH`
- `ENEMY_SPAWN`, `ENEMY_SIGHT`, `ENEMY_ATTACK`, `ENEMY_DAMAGED`, `ENEMY_DEATH`
- `WEAPON_FIRE`, `WEAPON_HIT`, `ITEM_PICKUP`
- `GAME_START`, `GAME_END`, `GAME_PAUSE`, `GAME_RESUME`

---

## Delta Compression

The protocol uses delta compression to optimize bandwidth:

1. **Full State**: Sent on game start or every 5 seconds
2. **Delta State**: Only changed fields are sent

```python
from networking.protocol import NetworkProtocol

protocol = NetworkProtocol()

# Server side
message = protocol.create_state_message(state_dict)

# Client side (reconstructs from delta)
delta = protocol.delta_state.update(new_state)
```

---

## Testing

```bash
# Unit tests
source .venv/bin/activate
python -m pytest tests/unit/ -v

# E2E tests
node tests/e2e/game.test.js
```

**Test Results:**
- Unit Tests: 49 passing
- E2E Tests: 16 passing

---

## External Dependencies

### Python
- `websockets` - WebSocket server
- `asyncio` - Async I/O (stdlib)

### JavaScript (Browser)
- HTML5 Canvas API
- WebSocket API
- requestAnimationFrame

### npm
- `playwright` - E2E testing
