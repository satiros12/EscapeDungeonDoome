# WebDoom - Architecture

## Overview

WebDoom is now a Pygame-based desktop FPS game (DOOM-style):
- **Platform**: Python 3 + Pygame
- **Rendering**: Raycasting pseudo-3D engine
- **Architecture**: Single-process game with integrated engine

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PYGAME APPLICATION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      main.py (Entry Point)                      │   │
│  │  - pygame.init()                                                │   │
│  │  - Game loop (60 FPS)                                           │   │
│  │  - Event handling                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                       │
│                                ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Game (Facade)                              │   │
│  │  - input_handler: InputHandler                                  │   │
│  │  - engine: GameEngine                                           │   │
│  │  - renderer: Renderer                                           │   │
│  │  - hud: HUD                                                     │   │
│  │  - console: Console                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │              │            │              │                  │
│  ┌──────┴──────┐ ┌─────┴─────┐ ┌───┴────┐ ┌───────┴───────┐         │
│  │   Renderer  │ │ InputHandler│ │  UI   │ │  GameEngine   │         │
│  │             │ │            │ │       │ │               │         │
│  │ - Raycast  │ │ - Keyboard │ │-Menu  │ │ - player_sys  │         │
│  │ - Sprites  │ │ - Mouse    │ │-HUD   │ │ - enemy_sys   │         │
│  │ - Draw     │ │            │ │-Console│ │ - combat_sys  │         │
│  └────────────┘ └────────────┘ └───────┘ └───────────────┘         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    GameEngine (Systems)                      │   │
│  ├─────────────────┬─────────────────┬─────────────────┬───────┤   │
│  │ PlayerSystem    │ EnemyAISystem   │ CombatSystem    │Physics│   │
│  └─────────────────┴─────────────────┴─────────────────┴───────┘   │
│                                │                                    │
│  ┌─────────────────────────────┴─────────────────────────────┐   │
│  │                    GameState (State)                         │   │
│  │  - player, enemies[], corpses[], map, game_mode             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
WebDoom/
├── src/                          # Main source code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── game.py                   # Game facade
│   ├── config.py                 # Configuration
│   ├── input_handler.py          # Input handling
│   ├── renderer.py               # Raycasting renderer
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── menu.py               # Main menu
│   │   ├── hud.py                # Heads-up display
│   │   └── console.py            # Debug console
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── game_engine.py        # GameEngine (facade)
│   │   ├── game_state.py         # Game state
│   │   └── event_system.py       # Event dispatcher
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── base.py               # System base class
│   │   ├── player_system.py      # Player movement
│   │   ├── enemy_ai_system.py    # Enemy AI
│   │   ├── combat_system.py      # Combat mechanics
│   │   └── weapon_system.py      # Weapons
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── physics.py            # Physics engine
│   │   └── raycasting.py         # Raycasting algorithms
│   ├── factory/
│   │   ├── __init__.py
│   │   └── entity_factory.py     # Entity creation
│   └── sprites/
│       ├── __init__.py
│       └── player.py             # Player sprite
│
├── data/                         # Game data
│   └── map-data.json             # Map definitions
│
├── assets/                       # Game assets
│   ├── sprites/                  # Sprites
│   ├── textures/                # Textures
│   └── fonts/                   # Fonts
│
├── tests/                        # Tests
│   ├── unit/                    # Unit tests (pytest)
│   │   ├── test_physics.py
│   │   ├── test_ai.py
│   │   ├── test_combat.py
│   │   ├── test_systems.py
│   │   └── test_config.py
│   └── integration/             # Integration tests
│       ├── test_game_loop.py
│       └── test_gameplay.py
│
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
└── README.md
```

---

## Module Responsibilities

### Core (src/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `main.py` | Entry point, game loop, event handling | pygame, game |
| `game.py` | Game facade, component coordination | engine, renderer, input |
| `config.py` | Game configuration constants | none |
| `input_handler.py` | Keyboard/mouse input | pygame |
| `renderer.py` | Raycasting rendering | pygame |

### Engine (src/engine/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `game_engine.py` | System orchestration, game loop | game_state, event_system |
| `game_state.py` | Entities, state, map parsing | none |
| `event_system.py` | Event dispatcher | none |

### Systems (src/systems/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `player_system.py` | Player movement | physics |
| `enemy_ai_system.py` | Enemy AI behaviors | physics |
| `combat_system.py` | Combat mechanics | event_system |
| `weapon_system.py` | Weapons + Items | event_system |
| `base.py` | Base system interface | none |

### Physics (src/physics/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `physics.py` | Collisions, line of sight, raycasting | game_state |
| `raycasting.py` | Raycasting algorithms | none |

---

## Design Patterns

| Pattern | Implementation |
|---------|---------------|
| **Facade** | `Game` (main), `GameEngine` |
| **Observer** | `EventSystem` notifies listeners |
| **Factory** | `EntityFactory` creates entities |
| **ECS-light** | Systems operate on entity collections |

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
| `searching` | Looking for player |
| `chase` | Pursues player |
| `attack` | Attacks player |
| `dying` | Death animation |
| `dead` | Corpse remains |

---

## Weapons

| Weapon | Type | Damage | Range | Cooldown |
|--------|------|--------|-------|----------|
| Fists | Melee | 10 | 1.5 | 0.5s |
| Chainsaw | Melee | 25 | 1.5 | 0.2s |
| Shotgun | Projectile | 10/pellet | 8.0 | 1.0s |
| Chaingun | Projectile | 8 | 15.0 | 0.1s |

---

## Controls

| Key | Action |
|-----|--------|
| W | Move forward |
| S | Move backward |
| A | Strafe left |
| D | Strafe right |
| ← | Rotate left |
| → | Rotate right |
| Space | Attack |
| ESC | Pause/Menu |
| P | Console (debug) |

---

## Event System

```python
from engine.event_system import EventSystem, EventType

dispatcher = EventSystem()

# Subscribe to events
dispatcher.subscribe(EventType.ENEMY_DEATH, on_enemy_death)

# Emit events
dispatcher.emit(EventType.PLAYER_ATTACK, {"target": enemy})

# Process queue
dispatcher.process_events()
```

**Event Types:**
- `GAME_START`, `GAME_WIN`, `GAME_OVER`, `PLAYER_DEATH`
- `PLAYER_DAMAGE`, `ENEMY_DEATH`, `ENEMY_HIT`
- `WEAPON_FIRE`, `WEAPON_HIT`, `ITEM_PICKUP`

---

## Testing

```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# All tests
python -m pytest tests/ -v
```

**Test Results:**
- Unit Tests: 85+ passing
- Integration Tests: 12+ passing

---

## External Dependencies

### Python
- `pygame>=2.5.0` - Game framework
- `pytest>=7.0.0` - Testing
- `pytest-cov>=4.0.0` - Coverage

---

## Running the Game

```bash
# Install dependencies
pip install -r requirements.txt

# Run game
python -m src.game

# Or directly
python src/main.py
```