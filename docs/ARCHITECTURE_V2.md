# WebDoom Architecture V2 - Proposal

## Executive Summary

The current architecture has served well for the MVP but exhibits significant limitations for future expansion. This proposal outlines a modular, object-oriented architecture that addresses these constraints while enabling advanced game features.

---

## Current Architecture Analysis

### Critical Issues Identified

| Issue | Impact | Severity |
|-------|--------|----------|
| Global variables everywhere (client) | Hard to test, debug, maintain | High |
| Duplicated map data (server/client) | Sync issues, data inconsistency | High |
| Monolithic modules (game_logic.py 219 lines) | Single responsibility violation | Medium |
| No proper state management | Unpredictable behavior | Medium |
| Tight coupling | Cannot swap components | Medium |
| No abstraction layers | Difficult to extend | Medium |

### Dependency Graph Problems

```
Server:
server.py → game_logic.py → game_state.py + physics.py
             └─ Mixed: movement + AI + combat in one class

Client:
main.js (global state) → ALL MODULES (circular dependencies)
```

---

## Proposed Architecture V2

### Core Design Principles

1. **Separation of Concerns** - Each module has one clear responsibility
2. **Loose Coupling** - Modules communicate through interfaces
3. **High Cohesion** - Related functionality grouped together
4. **Open/Closed** - Open for extension, closed for modification
5. **Testability** - Each component can be unit tested in isolation

---

## Object-Oriented Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVER (Python)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐      ┌─────────────────────┐                      │
│  │   IGameEngine       │      │   IGameState        │                      │
│  │   (Interface)       │      │   (Interface)       │                      │
│  ├─────────────────────┤      ├─────────────────────┤                      │
│  │ + update(dt)        │      │ + get_state()       │                      │
│  │ + reset()           │      │ + set_state()       │                      │
│  └──────────┬──────────┘      └──────────┬──────────┘                      │
│             │                            │                                  │
│             ▼                            ▼                                  │
│  ┌─────────────────────┐      ┌─────────────────────┐                      │
│  │   GameEngine        │◄─────│   GameStateManager │                      │
│  │                     │      │                     │                      │
│  │ - player_system     │      │ - player            │                      │
│  │ - enemy_system      │      │ - enemies[]         │                      │
│  │ - physics_engine    │      │ - map               │                      │
│  │ - event_manager     │      │ - game_mode         │                      │
│  └──────────┬──────────┘      └─────────────────────┘                      │
│             │                                                              │
│  ┌──────────┴──────────┐                                                   │
│  │   ISystem           │                                                   │
│  │   (Abstract Base)   │                                                   │
│  ├─────────────────────┤                                                   │
│  │ + update(dt)        │                                                   │
│  │ + on_event(event)  │                                                   │
│  └─────────────────────┘                                                   │
│             ▲                                                              │
│  ┌──────────┴─────────────────────────────────────────────────────┐        │
│  │                     CONCRETE SYSTEMS                           │        │
│  ├─────────────────┬─────────────────┬─────────────────┬────────────┤        │
│  │ PlayerMovement  │ EnemyAI         │ CombatSystem   │ Physics    │        │
│  │ System         │ System          │                │ Engine     │        │
│  └─────────────────┴─────────────────┴─────────────────┴────────────┘        │
│                                                                             │
│  ┌─────────────────────┐      ┌─────────────────────┐                      │
│  │   Map               │      │   EntityFactory    │                      │
│  │   (Value Object)    │      │   (Factory Pattern) │                      │
│  │                     │      │                     │                      │
│  │ - grid              │      │ + create_player()  │                      │
│  │ - width/height      │      │ + create_enemy()   │                      │
│  │ - get_tile(x,y)     │      │ + create_item()    │                      │
│  └─────────────────────┘      └─────────────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT (JavaScript)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Game (Facade/Singleton)                        │   │
│  │  - renderer: Renderer                                              │   │
│  │  - inputManager: InputManager                                       │   │
│  │  - networkManager: NetworkManager                                    │   │
│  │  - uiManager: UIManager                                             │   │
│  │  - state: GameState                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                    │                    │                    │                │
│  ┌────────────────┴────────┐  ┌────────┴────────┐  ┌───────┴────────┐        │
│  │     Renderer           │  │   InputManager │  │ NetworkManager │        │
│  │                        │  │                │  │                │        │
│  │ - Camera               │  │ - Keyboard    │  │ - WebSocket   │        │
│  │ - WallRenderer         │  │ - Mouse       │  │ - Protocol     │        │
│  │ - SpriteRenderer       │  │ - Touch       │  │ - Reconnector │        │
│  │ - EffectRenderer       │  │                │  │                │        │
│  └─────────────────────────┘  └────────────────┘  └────────────────┘        │
│                                                                             │
│  ┌─────────────────────────┐  ┌──────────────────────────────────────┐    │
│  │      UIManager          │  │         GameState (Observable)       │    │
│  │                        │  │                                      │    │
│  │ - ScreenManager        │  │  - player: Player                    │    │
│  │ - HUDManager           │  │  - enemies: Enemy[]                  │    │
│  │ - ConsoleManager       │  │  - items: Item[]                      │    │
│  │ - NotificationManager  │  │  - observers: Observer[]              │    │
│  └─────────────────────────┘  └──────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RENDERING HIERARCHY                               │   │
│  ├─────────────────┬─────────────────┬─────────────────┬────────────┤   │
│  │ Camera2D       │ WallRenderer    │ SpriteRenderer  │ ParticleSys│   │
│  │                │                 │                 │            │   │
│  │ - position     │ - raycaster     │ - billboard     │ - effects  │   │
│  │ - rotation     │ - texturer      │ - depth-sort    │ - pools    │   │
│  │ - fov          │ - lighting      │ - animation     │            │   │
│  └─────────────────┴─────────────────┴─────────────────┴────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          SHARED (Protocol)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Message Protocol (JSON)                          │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Client → Server:                                                  │   │
│  │  { "type": "input", "data": { "keys": {...}, "mouse": {...} } }   │   │
│  │  { "type": "action", "action": "attack", "target": "enemy_1" }     │   │
│  │  { "type": "chat", "message": "hello" }                           │   │
│  │                                                                     │   │
│  │  Server → Client:                                                  │   │
│  │  { "type": "state", "data": { "player": {...}, "delta": {...} } }  │   │
│  │  { "type": "event", "event": "enemy_died", "data": {...} }         │   │
│  │  { "type": "sync", "timestamp": 1234567890 }                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## New Directory Structure

```
WebDoom/
├── public/                          # Frontend static files
│   ├── index.html
│   └── js/
│       ├── main.js                  # Entry point
│       ├── game.js                  # Game facade/class
│       ├── core/
│       │   ├── game-state.js        # Observable state
│       │   ├── observable.js        # Observer pattern
│       │   └── constants.js         # Shared constants
│       ├── systems/
│       │   ├── renderer.js           # Main renderer
│       │   ├── camera.js            # Camera calculations
│       │   ├── input-manager.js     # Unified input
│       │   ├── network-manager.js   # WebSocket handling
│       │   └── ui-manager.js        # UI management
│       ├── rendering/
│       │   ├── wall-renderer.js     # Wall rendering
│       │   ├── sprite-renderer.js   # Sprite rendering
│       │   ├── effect-renderer.js   # Particles/effects
│       │   └── raycaster.js         # Raycasting engine
│       └── entities/
│           ├── player.js            # Player entity
│           ├── enemy.js             # Enemy entity
│           └── corpse.js            # Corpse entity
│
├── src/
│   └── server/
│       ├── __init__.py
│       ├── main.py                  # Entry point
│       ├── game-engine.py           # Main game engine
│       ├── core/
│       │   ├── interfaces.py        # Abstract interfaces
│       │   ├── entity.py            # Base entity class
│       │   └── event-system.py      # Event dispatcher
│       ├── systems/
│       │   ├── base.py              # ISystem base class
│       │   ├── player-system.py     # Player logic
│       │   ├── enemy-ai-system.py   # Enemy AI
│       │   ├── combat-system.py     # Combat logic
│       │   └── physics-engine.py    # Physics
│       ├── state/
│       │   ├── game-state-manager.py
│       │   ├── map.py               # Map value object
│       │   └── entities/            # Entity classes
│       │       ├── player.py
│       │       ├── enemy.py
│       │       └── item.py
│       ├── networking/
│       │   ├── protocol.py          # Message protocol
│       │   ├── websocket-handler.py
│       │   └── http-server.py
│       ├── factory/
│       │   └── entity-factory.py    # Entity creation
│       └── config/
│           ├── settings.py
│           └── constants.py
│
├── shared/                          # Shared code between server/client
│   ├── map-data.json                # Single source of map truth
│   ├── protocol.json                # Message protocol schema
│   └── constants.js                 # Shared constants
│
├── tests/
│   ├── unit/
│   │   ├── server/
│   │   └── client/
│   └── e2e/
│
└── docs/
    └── ARCHITECTURE_V2.md
```

---

## Design Patterns Applied

### 1. Facade Pattern (Server & Client)
- **Purpose**: Simplify complex subsystem interfaces
- **Implementation**: `GameEngine` (server), `Game` (client)

### 2. Observer Pattern
- **Purpose**: Decouple state changes from UI updates
- **Implementation**: `Observable` / `GameState` notifies observers

### 3. Factory Pattern
- **Purpose**: Encapsulate entity creation
- **Implementation**: `EntityFactory` creates all game entities

### 4. Strategy Pattern
- **Purpose**: Interchangeable AI behaviors
- **Implementation**: `IEnemyBehavior` with concrete implementations

### 5. Command Pattern
- **Purpose**: Encapsulate actions as objects
- **Implementation**: Network messages as commands

### 6. Entity-Component-System (ECS) Light
- **Purpose**: Flexible entity composition
- **Implementation**: Systems operate on entity collections

### 7. State Pattern
- **Purpose**: Manage game states cleanly
- **Implementation**: `GameState` with state machine

---

## Key Module Specifications

### Server - Systems

```python
# systems/base.py
class ISystem(ABC):
    @abstractmethod
    def update(self, dt: float) -> None:
        pass
    
    @abstractmethod
    def on_event(self, event: GameEvent) -> None:
        pass

# systems/player-system.py
class PlayerMovementSystem(ISystem):
    def __init__(self, physics: IPhysics, map: IMap):
        self.physics = physics
        self.map = map
    
    def update(self, dt: float) -> None:
        # Process player movement
        pass
    
    def on_event(self, event: GameEvent) -> None:
        if event.type == EventType.PLAYER_INPUT:
            self.handle_input(event.data)

# systems/enemy-ai-system.py
class EnemyAISystem(ISystem):
    def __init__(self, player: IPlayer, physics: IPhysics, behavior_factory: IBehaviorFactory):
        self.player = player
        self.physics = physics
        self.behaviors = {}
    
    def register_enemy(self, enemy_id: str, behavior_type: BehaviorType) -> None:
        self.behaviors[enemy_id] = self.behavior_factory.create(behavior_type)
```

### Client - Game State

```javascript
// core/observable.js
class Observable {
    constructor() {
        this.observers = new Set();
    }
    
    subscribe(observer) {
        this.observers.add(observer);
    }
    
    unsubscribe(observer) {
        this.observers.delete(observer);
    }
    
    notify(event) {
        this.observers.forEach(o => o.onEvent(event));
    }
}

// core/game-state.js
class GameState extends Observable {
    constructor() {
        super();
        this.player = null;
        this.enemies = new Map();
        this.corpses = [];
    }
    
    updateFromServer(data) {
        this.player = data.player;
        // Delta compression - only update changed entities
        data.enemies.forEach(e => {
            this.enemies.set(e.id, e);
        });
        this.notify({ type: 'state_updated', data });
    }
}
```

---

## Communication Protocol V2

### Message Format (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "enum": ["input", "action", "state", "event", "sync"] },
    "timestamp": { "type": "integer" },
    "data": { "type": "object" }
  }
}
```

### State Delta Protocol

```json
// Full state (initial load)
{
  "type": "state",
  "data": {
    "mode": "full",
    "player": { "id": "p1", "x": 1.5, "y": 1.5, "health": 100 },
    "enemies": [{ "id": "e1", "x": 5, "y": 3, "state": "chase" }],
    "timestamp": 1234567890
  }
}

// Delta state (updates only)
{
  "type": "state",
  "data": {
    "mode": "delta",
    "changes": {
      "player": { "health": 90 },
      "enemies": {
        "e1": { "state": "dead" },
        "e2": { "x": 4.5, "y": 3.2 }
      }
    },
    "removed": ["enemy:e3"],
    "timestamp": 1234567891
  }
}
```

---

## Extensibility Examples

### Adding a New Enemy Type

```python
# server/systems/enemy-ai-system.py
class EnemyAISystem:
    BEHAVIOR_REGISTRY = {
        BehaviorType.PATROL: PatrolBehavior,
        BehaviorType.CHASE: ChaseBehavior,
        BehaviorType.FLANKER: FlankerBehavior,  # NEW
        BehaviorType.SHOOTER: ShooterBehavior,  # NEW
    }
    
# Configuration-driven enemy spawning
ENEMY_CONFIGS = {
    "imp": { "health": 30, "behavior": BehaviorType.CHASE, "damage": 10 },
    "demon": { "health": 60, "behavior": BehaviorType.FLANKER, "damage": 15 },
    "cacodemon": { "health": 100, "behavior": BehaviorType.SHOOTER, "damage": 20 },
}
```

### Adding a New Weapon

```python
# server/systems/combat-system.py
class Weapon(ABC):
    @abstractmethod
    def fire(self, attacker: Entity, target: Entity) -> DamageResult:
        pass

class Shotgun(Weapon):
    def fire(self, attacker, target):
        # Multiple pellets, spread calculation
        pellets = 8
        hits = sum(1 for _ in range(pellets) if random.random() < 0.7)
        return DamageResult(damage=hits * 10, hit_count=hits)
```

---

## Migration Path

### Phase 1: Foundation (Weeks 1-2)
1. Create shared/constants.py with single map source
2. Implement observable pattern on client
3. Create entity interfaces

### Phase 2: Server Refactor (Weeks 3-4)
1. Extract systems from game_logic.py
2. Implement event system
3. Create factory pattern for entities

### Phase 3: Client Refactor (Weeks 5-6)
1. Create Game facade class
2. Modularize renderer
3. Implement observer pattern

### Phase 4: Protocol Enhancement (Week 7)
1. Implement delta compression
2. Add event-based messaging
3. Optimize bandwidth

---

## Testing Strategy

| Layer | Test Type | Coverage Target |
|-------|-----------|-----------------|
| Systems (Python) | Unit | 80% |
| Physics | Unit | 90% |
| AI Behaviors | Integration | 70% |
| Client State | Unit | 80% |
| Renderer | Manual/Visual | N/A |
| E2E | Playwright | Critical paths |

---

## Performance Targets

| Metric | Current | Target |
|--------|---------|--------|
| Server tick rate | 60 FPS | 60 FPS |
| Network bandwidth | ~10KB/s | ~2KB/s (delta) |
| Client FPS | 60 FPS | 60 FPS |
| Memory (client) | TBD | <50MB |
| Code coverage | 0% | 70% |

---

## Summary

This architecture addresses the current limitations while providing:

1. **Maintainability** - Clear separation of concerns
2. **Testability** - Mockable interfaces, isolated components
3. **Extensibility** - Easy to add enemies, weapons, items
4. **Performance** - Delta compression, optimized rendering
5. **Scalability** - Multiplayer-ready protocol design

The modular design allows individual components to be developed, tested, and optimized independently, significantly improving the development velocity for future features.
