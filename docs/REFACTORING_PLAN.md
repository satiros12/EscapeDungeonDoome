# WebDoom Architecture Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring plan for WebDoom's architecture. The primary goals are:

1. **Integrate existing systems** - Make GameEngine actually use the systems in `src/systems/`
2. **Build proper OOP architecture** - Implement clean entity-component patterns
3. **Improve all modules** - UI, Physics, Input Handling
4. **Enhanced documentation** - Both architectural diagrams and code-first API docs

---

## Current Architecture Problems

### Problem 1: Duplicate/Unused Systems

**Location**: `src/systems/` (unused) vs `src/engine/game_engine.py` (inline)

The codebase contains two parallel implementations:

- `src/systems/`: PlayerSystem, EnemyAISystem, CombatSystem - properly designed but **never used**
- `src/engine/game_engine.py`: Has its own inline implementations that bypass the systems

**Impact**: Code duplication, confusion, dead code

### Problem 2: Tight Coupling

```
GameEngine → GameState (direct)
GameEngine → Physics (direct)
GameEngine → EventSystem (minimal use)
```

All components are tightly coupled, making:
- Unit testing impossible
- Swapping implementations difficult
- Extensibility limited

### Problem 3: Missing OOP Patterns

- No clear Entity abstraction
- No Component interfaces
- No System registry/update loop
- GameState is a "god object"

### Problem 4: Inconsistent Documentation

- ARCHITECTURE.md describes intended architecture
- Actual code doesn't match
- No API documentation for developers

---

## Phase 1: Core Architecture Refactoring

### 1.1 Entity-Component-System (ECS) Architecture

**Goal**: Implement proper ECS pattern where GameEngine orchestrates systems

**New Architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        GameEngine                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SystemRegistry                                          │   │
│  │  - player_system: PlayerSystem                           │   │
│  │  - enemy_ai_system: EnemyAISystem                        │   │
│  │  - combat_system: CombatSystem                           │   │
│  │  - physics: Physics                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐    ┌─────────────────┐   ┌────────────┐       │
│  │ PlayerSystem│    │EnemyAISystem   │   │CombatSystem│       │
│  │ - movement  │    │ - behaviors    │   │ - damage   │       │
│  │ - input     │    │ - states       │   │ - weapons  │       │
│  └─────────────┘    └─────────────────┘   └────────────┘       │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    GameState                             │   │
│  │  - entities: Dict[str, Entity]                          │   │
│  │  - components: Dict[str, Component]                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Tasks**:

| Task | Description | Priority |
|------|-------------|----------|
| T1.1 | Create Entity base class | High |
| T1.2 | Create Component abstract classes | High |
| T1.3 | Refactor GameEngine to use SystemRegistry | High |
| T1.4 | Connect existing systems to GameEngine | High |
| T1.5 | Remove inline implementations from GameEngine | Medium |

### 1.2 Entity Definitions

**Current**: Player and Enemy are dataclasses in game_state.py

**Target**: Proper Entity subclasses with Component access

```python
# New entity structure
class Entity(ABC):
    """Base class for all game entities."""
    id: str
    components: Dict[str, Component]
    
    def get_component(self, name: str) -> Optional[Component]: ...
    def add_component(self, component: Component): ...
    def remove_component(self, name: str): ...

class PlayerEntity(Entity):
    """Player entity with specialized components."""
    def __init__(self):
        self.add_component(PositionComponent(1.5, 1.5, 0.0))
        self.add_component(HealthComponent(100))
        self.add_component(PlayerInputComponent())
        self.add_component(WeaponComponent("fists"))

class EnemyEntity(Entity):
    """Enemy entity with AI components."""
    def __init__(self, enemy_type: str):
        self.add_component(PositionComponent(x, y, 0.0))
        self.add_component(HealthComponent(30))
        self.add_component(AIComponent(enemy_type))
        self.add_component(CombatComponent())
```

**Implementation Tasks**:

| Task | Description | Priority |
|------|-------------|----------|
| T1.6 | Create Entity base class | High |
| T1.7 | Create Component classes (Position, Health, AI, etc.) | High |
| T1.8 | Refactor Player to PlayerEntity | High |
| T1.9 | Refactor Enemy to EnemyEntity | High |
| T1.10 | Update GameState to use entities | High |

---

## Phase 2: System Integration

### 2.1 PlayerSystem Integration

**Current State**: Unused, has its own logic

**Target**: Used by GameEngine for all player operations

**Integration Plan**:
1. Remove duplicate player logic from GameEngine._update_player()
2. Create SystemRegistry in GameEngine
3. Call player_system.update(dt) in game loop
4. Pass GameState to PlayerSystem on init

**Code Changes**:

```python
# Before (game_engine.py)
def _update_player(self, dt: float) -> None:
    # Inline movement logic
    if keys.get("KeyW", False):
        move_x += math.cos(player.angle) * PLAYER_SPEED * dt
    # ... 50 more lines

# After (game_engine.py)
def update(self, dt: float) -> None:
    self.system_registry.player_system.update(dt)
```

### 2.2 EnemyAISystem Integration

**Target**: All enemy behaviors delegated to EnemyAISystem

**Integration Plan**:
1. Remove enemy update logic from GameEngine._update_enemies()
2. Wire EnemyAISystem to handle all AI states
3. Use physics for collision and LOS

### 2.3 CombatSystem Integration

**Target**: All combat logic in CombatSystem

**Integration Plan**:
1. Move attack logic from GameEngine._check_combat()
2. Handle hit effects and death animations
3. Manage weapon cooldowns

---

## Phase 3: UI Architecture Refactoring

### 3.1 Current Problems

- Menu, HUD, Console tightly coupled to Game class
- No clear interface for UI components
- Mixed rendering responsibilities

### 3.2 New Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        UIManager                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ MenuSystem │  │ HUDSystem   │  │ ConsoleSystem           │  │
│  │             │  │             │  │                         │  │
│  │ - main_menu│  │ - health_bar│  │ - command_parser        │  │
│  │ - options  │  │ - kills     │  │ - output_buffer         │  │
│  │ - callbacks│  │ - weapons   │  │ - input_history         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 UI Interface Definition

```python
class IUIComponent(ABC):
    """Base interface for all UI components."""
    
    @abstractmethod
    def update(self, dt: float) -> None: ...
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None: ...
    
    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> bool: ...
    
    @abstractmethod
    def show(self) -> None: ...
    
    @abstractmethod
    def hide(self) -> None: ...

class IUIManager(ABC):
    """Interface for UI management."""
    
    @abstractmethod
    def register(self, name: str, component: IUIComponent): ...
    
    @abstractmethod
    def get(self, name: str) -> Optional[IUIComponent]: ...
    
    @abstractmethod
    def set_active(self, name: str): ...
    
    @abstractmethod
    def update(self, dt: float): ...
    
    @abstractmethod
    def render(self, surface: pygame.Surface): ...
```

### 3.4 Implementation Tasks

| Task | Description | Priority |
|------|-------------|----------|
| T3.1 | Create IUIComponent interface | High |
| T3.2 | Create IUIManager interface | High |
| T3.3 | Refactor Menu to implement IUIComponent | High |
| T3.4 | Refactor HUD to implement IUIComponent | High |
| T3.5 | Refactor Console to implement IUIComponent | High |
| T3.6 | Create UIManager class | High |
| T3.7 | Update Game to use UIManager | Medium |

---

## Phase 4: Physics Module Refactoring

### 4.1 Current Problems

- Physics directly coupled to GameState
- No interface for swapping implementations
- Raycasting mixed with collision detection

### 4.2 New Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      IPhysics Interface                         │
├─────────────────────────────────────────────────────────────────┤
│  is_wall(x, y) -> bool                                          │
│  has_line_of_sight(x1, y1, x2, y2) -> bool                      │
│  cast_ray(origin, direction) -> RayResult                      │
│  check_collision(entity) -> bool                                │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ RaycastPhysics │           │ AStarPhysics    │
    │ (current impl) │           │ (future path)   │
    └─────────────────┘           └─────────────────┘
```

### 4.3 Component-Based Physics

```python
class ICollidable(ABC):
    """Component for entities that can collide."""
    @abstractmethod
    def get_collision_radius(self) -> float: ...
    
    @abstractmethod
    def on_collision(self, other: "Entity") -> None: ...

class PositionComponent(Component):
    """Component for position and movement."""
    x: float
    y: float
    angle: float
    
    def move(self, dx: float, dy: float): ...
    def rotate(self, da: float): ...
    def get_position(self) -> Tuple[float, float]: ...
```

### 4.4 Implementation Tasks

| Task | Description | Priority |
|------|-------------|----------|
| T4.1 | Create IPhysics interface | High |
| T4.2 | Create Collidable component | High |
| T4.3 | Refactor Physics to implement IPhysics | High |
| T4.4 | Add PositionComponent to entities | High |
| T4.5 | Decouple Physics from GameState | Medium |

---

## Phase 5: Input Handling Refactoring

### 5.1 Current Problems

- InputHandler is simple, but not integrated with systems
- No input mapping abstraction
- Keyboard state managed in Game, not systems

### 5.2 New Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      InputManager                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ KeyBindingMap  │  │ InputState     │  │ ActionDispatcher │  │
│  │                │  │                │  │                  │  │
│  │ W -> MOVE_FWD  │  │ pressed: Set   │  │ on_action()      │  │
│  │ S -> MOVE_BACK │  │ held: Set     │  │ emit_event()    │  │
│  │ SPACE -> ATTACK│  │ released: Set  │  │                  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Implementation Tasks

| Task | Description | Priority |
|------|-------------|----------|
| T5.1 | Create InputAction enum | Medium |
| T5.2 | Create KeyBindingMap class | Medium |
| T5.3 | Refactor InputHandler to InputManager | Medium |
| T5.4 | Integrate with PlayerSystem | Medium |

---

## Phase 6: Documentation Improvements

### 6.1 New ARCHITECTURE.md Structure

```markdown
# WebDoom - Architecture

## Overview
[Game description and goals]

## Architecture Diagram
[ASCII diagrams]

## Module Responsibilities
[Tables with module details]

## API Reference
[Code-first documentation]

## Class Hierarchy
[Inheritance diagrams]

## Usage Examples
[Code snippets]
```

### 6.2 API Documentation Format

```python
class GameEngine:
    """
    Core game engine coordinating all systems.
    
    The GameEngine is the main entry point for game logic, 
    managing the update loop and coordinating between systems.
    
    Example:
        >>> engine = GameEngine(screen)
        >>> engine.start_game()
        >>> while running:
        ...     engine.update(dt)
        ...     engine.render()
    
    Attributes:
        state: Current GameState instance
        system_registry: Registry of all game systems
        event_system: Event dispatcher for game events
    """
    
    def __init__(self, screen: pygame.Surface) -> None:
        """
        Initialize the game engine.
        
        Args:
            screen: Pygame surface for rendering
            
        Raises:
            RuntimeError: If pygame not initialized
        """
        ...
```

### 6.3 Implementation Tasks

| Task | Description | Priority |
|------|-------------|----------|
| T6.1 | Rewrite ARCHITECTURE.md with new diagrams | High |
| T6.2 | Add API documentation to all public classes | High |
| T6.3 | Add docstrings to all public methods | Medium |
| T6.4 | Create inline code examples | Medium |

---

## Implementation Roadmap

### Phase 1: Core (Week 1)
- Create Entity/Component base classes
- Implement SystemRegistry
- Integrate existing systems

### Phase 2: UI (Week 1-2)
- Refactor Menu, HUD, Console
- Create UIManager

### Phase 3: Physics & Input (Week 2)
- Create IPhysics interface
- Refactor InputManager

### Phase 4: Documentation (Week 2-3)
- Rewrite ARCHITECTURE.md
- Add API docs

---

## Task Distribution

### code-writer Tasks
- T1.1, T1.2, T1.3, T1.4, T1.5 (Core ECS)
- T1.6, T1.7, T1.8, T1.9, T1.10 (Entities)
- T3.1, T3.2, T3.3, T3.4, T3.5, T3.6, T3.7 (UI)
- T4.1, T4.2, T4.3, T4.4 (Physics)
- T5.1, T5.2, T5.3, T5.4 (Input)

### documenter Tasks
- T6.1, T6.2, T6.3, T6.4 (Documentation)

---

## Success Criteria

1. **Systems Integration**: GameEngine uses all systems from src/systems/
2. **Clean Architecture**: Clear separation between Engine, State, Systems, UI
3. **Testability**: All major components have interfaces for mocking
4. **Documentation**: ARCHITECTURE.md matches actual code structure
5. **No Code Duplication**: Inline implementations removed, systems used

---

## Dependencies

```python
# New imports structure
from engine.game_engine import GameEngine
from engine.game_state import GameState
from engine.system_registry import SystemRegistry
from entities.base import Entity, Component
from entities.player import PlayerEntity
from entities.enemy import EnemyEntity
from systems.base import SystemBase, ISystem
from systems.player_system import PlayerSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.combat_system import CombatSystem
from physics.interfaces import IPhysics
from physics.raycast import RaycastPhysics
from ui.interfaces import IUIComponent, IUIManager
from ui.manager import UIManager
from input.manager import InputManager
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing gameplay | High | Keep old code until new is tested |
| Over-engineering | Medium | Keep patterns simple, avoid abstractitis |
| Documentation drift | Low | Auto-generate API docs where possible |
| Integration failures | High | Test each system individually |

---

## Appendix: File Structure After Refactoring

```
src/
├── __init__.py
├── main.py                    # Entry point (unchanged)
├── config.py                  # Configuration (unchanged)
├── game.py                    # Facade (simplified)
│
├── engine/                    # Game engine core
│   ├── __init__.py
│   ├── game_engine.py         # Main engine (refactored)
│   ├── game_state.py          # State (refactored to use entities)
│   ├── event_system.py        # Events (keep)
│   ├── system_registry.py    # NEW - System management
│   └── interfaces.py         # NEW - Abstract interfaces
│
├── entities/                  # NEW - Entity system
│   ├── __init__.py
│   ├── base.py               # Entity, Component bases
│   ├── player.py            # PlayerEntity
│   ├── enemy.py              # EnemyEntity
│   └── factory.py            # EntityFactory
│
├── systems/                   # Game systems (integrated)
│   ├── __init__.py
│   ├── base.py               # SystemBase, ISystem
│   ├── player_system.py     # PlayerSystem (integrated)
│   ├── enemy_ai_system.py   # EnemyAISystem (integrated)
│   ├── combat_system.py     # CombatSystem (integrated)
│   └── weapon_system.py     # WeaponSystem
│
├── physics/                  # Physics module (refactored)
│   ├── __init__.py
│   ├── interfaces.py        # NEW - IPhysics
│   ├── raycast.py           # Raycasting algorithms
│   ├── physics.py          # Physics implementation
│   └── collisions.py       # Collision detection
│
├── ui/                       # UI module (refactored)
│   ├── __init__.py
│   ├── interfaces.py        # NEW - IUIComponent, IUIManager
│   ├── manager.py          # NEW - UIManager
│   ├── menu.py             # Menu (refactored)
│   ├── hud.py              # HUD (refactored)
│   └── console.py          # Console (refactored)
│
├── input/                    # NEW - Input management
│   ├── __init__.py
│   ├── manager.py          # InputManager
│   ├── bindings.py         # KeyBindingMap
│   └── actions.py          # InputAction enum
│
└── renderer.py              # Renderer (minor changes)
```