# WebDoom - Architecture

## Overview

WebDoom is a Pygame-based desktop FPS game (DOOM-style) with:
- **Platform**: Python 3 + Pygame
- **Rendering**: Raycasting pseudo-3D engine
- **Architecture**: Entity-Component-System (ECS) pattern with SystemRegistry
- **State**: Single-process game with integrated engine

---

## Architecture Diagram

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PYGAME APPLICATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         main.py (Entry Point)                         │  │
│  │  - pygame.init()                                                       │  │
│  │  - Game loop (60 FPS)                                                 │  │
│  │  - Event handling                                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                   │                                          │
│                                   ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           Game (Facade)                                │  │
│  │  - input_manager: InputManager                                         │  │
│  │  - engine: GameEngine                                                  │  │
│  │  - renderer: Renderer                                                 │  │
│  │  - ui_manager: UIManager                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│          │            │              │              │                      │
│  ┌───────┴───────┐    │      ┌───────┴───────┐      │                      │
│  │   Renderer    │    │      │   UIManager   │      │                      │
│  │               │    │      │               │      │                      │
│  │ - Raycast    │    │      │ - Menu        │      │                      │
│  │ - Sprites    │    │      │ - HUD         │      │                      │
│  │ - Draw       │    │      │ - Console     │      │                      │
│  └──────────────┘    │      └───────────────┘      │                      │
│                      │                              │                      │
│  ┌───────────────────┴──────────────────────────────┴───────────────────┐  │
│  │                            GameEngine                                  │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    SystemRegistry                               │  │  │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │  │  │
│  │  │  │PlayerSystem│ │EnemyAISystem│ │CombatSystem │ │ Physics  │ │  │  │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                │                                        │  │
│  │         ┌──────────────────────┼──────────────────────┐                │  │
│  │         ▼                      ▼                      ▼                │  │
│  │  ┌─────────────┐     ┌─────────────────┐    ┌────────────┐           │  │
│  │  │   Player    │     │  Enemy Entities │    │GameState  │           │  │
│  │  │  (Entity)   │     │    (Entities)    │    │           │           │  │
│  │  └─────────────┘     └─────────────────┘    └────────────┘           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Entity-Component-System (ECS) Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ECS ARCHITECTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           ENTITIES                                    │  │
│  │  ┌─────────────────────┐    ┌─────────────────────┐                   │  │
│  │  │    PlayerEntity     │    │   EnemyEntity       │                   │  │
│  │  │                     │    │                     │                   │  │
│  │  │ - PositionComponent │    │ - PositionComponent │                   │  │
│  │  │ - HealthComponent   │    │ - HealthComponent   │                   │  │
│  │  │ - CombatComponent   │    │ - AIComponent       │                   │  │
│  │  │ - PlayerInputComp   │    │ - CombatComponent   │                   │  │
│  │  └─────────────────────┘    └─────────────────────┘                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         COMPONENTS                                     │  │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐            │  │
│  │  │ PositionComp   │ │  HealthComp    │ │    AIComp      │            │  │
│  │  │ - x, y, angle  │ │ - health       │ │ - state        │            │  │
│  │  │ - move()       │ │ - take_damage()│ │ - target       │            │  │
│  │  │ - rotate()     │ │ - heal()       │ │ - patrol_dir   │            │  │
│  │  └────────────────┘ └────────────────┘ └────────────────┘            │  │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐            │  │
│  │  │  CombatComp    │ │PlayerInputComp │ │ CollidableComp │            │  │
│  │  │ - attack_range │ │ - keys         │ │ - radius       │            │  │
│  │  │ - attack_dmg   │ │ - is_attacking │ │ - on_collision │            │  │
│  │  │ - can_attack() │ │ - update_keys()│ │                │            │  │
│  │  └────────────────┘ └────────────────┘ └────────────────┘            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           SYSTEMS                                      │  │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐              │  │
│  │  │  PlayerSystem  │ │ EnemyAISystem  │ │  CombatSystem  │              │  │
│  │  │                │ │                │ │                │              │  │
│  │  │ - movement     │ │ - patrol       │ │ - player_attack│              │  │
│  │  │ - input        │ │ - chase        │ │ - enemy_attack │              │  │
│  │  │ - rotation     │ │ - attack       │ │ - damage       │              │  │
│  │  └────────────────┘ └────────────────┘ └────────────────┘              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### UI Manager Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UI MANAGER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           UIManager                                    │  │
│  │  Implements: IUIManager                                               │  │
│  ├───────────────────────────────────────────────────────────────────────┤  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────────┐  │  │
│  │  │    Menu        │  │      HUD       │  │       Console           │  │  │
│  │  │ (IUIComponent) │  │ (IUIComponent) │  │   (IUIComponent)        │  │  │
│  │  │                │  │                │  │                         │  │  │
│  │  │ - main_menu    │  │ - health_bar  │  │ - command_parser       │  │  │
│  │  │ - options      │  │ - kills       │  │ - output_buffer        │  │  │
│  │  │ - callbacks    │  │ - weapons     │  │ - input_history        │  │  │
│  │  └────────────────┘  └────────────────┘  └─────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       IUIComponent Interface                           │  │
│  │  + update(dt) -> None                                                 │  │
│  │  + render(surface) -> None                                           │  │
│  │  + handle_input(event) -> bool                                       │  │
│  │  + show() -> None                                                    │  │
│  │  + hide() -> None                                                    │  │
│  │  + active: bool (property)                                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Input Manager Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INPUT MANAGER ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         InputManager                                   │  │
│  │  ┌────────────────────────────────────────────────────────────────┐  │  │
│  │  │                     KeyBindingMap                              │  │  │
│  │  │                                                                  │  │  │
│  │  │   pygame.K_w    → InputAction.MOVE_FORWARD                     │  │  │
│  │  │   pygame.K_s    → InputAction.MOVE_BACKWARD                    │  │  │
│  │  │   pygame.K_a    → InputAction.MOVE_LEFT                        │  │  │
│  │  │   pygame.K_d    → InputAction.MOVE_RIGHT                       │  │  │
│  │  │   pygame.K_LEFT → InputAction.ROTATE_LEFT                      │  │  │
│  │  │   pygame.K_RIGHT→ InputAction.ROTATE_RIGHT                      │  │  │
│  │  │   pygame.K_SPACE→ InputAction.ATTACK                           │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                │                                       │  │
│  │         ┌──────────────────────┼──────────────────────┐              │  │
│  │         ▼                      ▼                      ▼              │  │
│  │  ┌─────────────┐     ┌─────────────────┐    ┌────────────┐         │  │
│  │  │ Key State   │     │  Action State   │    │   Mouse    │         │  │
│  │  │  (legacy)   │     │  (InputAction)   │    │   State    │         │  │
│  │  └─────────────┘     └─────────────────┘    └────────────┘         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Physics Interface Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHYSICS INTERFACE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      IPhysics Interface                               │  │
│  ├───────────────────────────────────────────────────────────────────────┤  │
│  │  + is_wall(x, y) -> bool                                             │  │
│  │  + has_line_of_sight(x1, y1, x2, y2) -> bool                        │  │
│  │  + cast_ray(angle, x, y) -> Dict[str, Any]                          │  │
│  │  + check_collision(x, y) -> bool                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                    ┌───────────────┴───────────────┐                       │
│                    ▼                               ▼                       │
│        ┌─────────────────────┐         ┌─────────────────────┐           │
│        │   Physics (Raycast)  │         │  Future: AStarPhysics│           │
│        │   (Current impl)     │         │  (Pathfinding)       │           │
│        └─────────────────────┘         └─────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
WebDoom/
├── src/                              # Main source code
│   ├── __init__.py
│   ├── main.py                       # Entry point
│   ├── game.py                       # Game facade
│   ├── config.py                     # Configuration
│   ├── renderer.py                   # Raycasting renderer
│   ├── input_handler.py              # Legacy input handler
│   │
│   ├── engine/                       # Game engine core
│   │   ├── __init__.py
│   │   ├── game_engine.py            # Main game engine
│   │   ├── game_state.py             # Game state management
│   │   ├── event_system.py           # Event dispatcher
│   │   └── system_registry.py        # System coordination
│   │
│   ├── entities/                     # Entity-Component System
│   │   ├── __init__.py
│   │   ├── base.py                   # Entity, Component bases
│   │   ├── components.py             # All component classes
│   │   ├── player.py                 # PlayerEntity
│   │   ├── enemy.py                  # EnemyEntity
│   │   └── factory.py                # EntityFactory
│   │
│   ├── systems/                      # Game systems
│   │   ├── __init__.py
│   │   ├── base.py                   # System base class
│   │   ├── player_system.py          # Player movement/input
│   │   ├── enemy_ai_system.py        # Enemy AI behaviors
│   │   ├── combat_system.py          # Combat mechanics
│   │   └── weapon_system.py          # Weapons
│   │
│   ├── physics/                      # Physics module
│   │   ├── __init__.py
│   │   ├── interfaces.py             # IPhysics interface
│   │   ├── physics.py                # Physics implementation
│   │   └── raycasting.py             # Raycasting algorithms
│   │
│   ├── ui/                           # UI module
│   │   ├── __init__.py
│   │   ├── interfaces.py             # IUIComponent, IUIManager
│   │   ├── manager.py                # UIManager
│   │   ├── menu.py                   # Main menu
│   │   ├── hud.py                    # Heads-up display
│   │   └── console.py                # Debug console
│   │
│   ├── input/                        # Input management
│   │   ├── __init__.py
│   │   ├── manager.py                # InputManager
│   │   ├── bindings.py               # KeyBindingMap
│   │   └── actions.py                # InputAction enum
│   │
│   └── sprites/                      # Sprite handling
│       ├── __init__.py
│       └── player.py                 # Player sprite
│
├── data/                             # Game data
│   └── map-data.json                 # Map definitions
│
├── assets/                           # Game assets
│   ├── sprites/                      # Sprites
│   ├── textures/                     # Textures
│   └── fonts/                        # Fonts
│
├── tests/                            # Tests
│   ├── unit/                         # Unit tests (pytest)
│   └── integration/                  # Integration tests
│
├── docs/                             # Documentation
├── requirements.txt                  # Python dependencies
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
| `renderer.py` | Raycasting rendering | pygame |

### Engine (src/engine/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `game_engine.py` | System orchestration, game loop | system_registry, game_state |
| `game_state.py` | Entities, state, map parsing | none |
| `event_system.py` | Event dispatcher | none |
| `system_registry.py` | System coordination and updates | systems |

### Entities (src/entities/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `base.py` | Entity and Component base classes | none |
| `components.py` | All component implementations | base |
| `player.py` | PlayerEntity with player components | base, components |
| `enemy.py` | EnemyEntity with AI components | base, components |
| `factory.py` | Entity creation factory | player, enemy |

### Systems (src/systems/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `base.py` | Base system interface (ISystem) | none |
| `player_system.py` | Player movement, input handling | game_state, physics, input |
| `enemy_ai_system.py` | Enemy AI behaviors and states | game_state, physics |
| `combat_system.py` | Combat mechanics and damage | game_state |
| `weapon_system.py` | Weapons and items | event_system |

### Physics (src/physics/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `interfaces.py` | IPhysics abstract interface | none |
| `physics.py` | Collision, line of sight, raycasting | game_state |
| `raycasting.py` | Raycasting algorithms | none |

### UI (src/ui/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `interfaces.py` | IUIComponent, IUIManager interfaces | pygame |
| `manager.py` | UI component coordination | interfaces |
| `menu.py` | Main menu with options | interfaces |
| `hud.py` | Heads-up display | interfaces |
| `console.py` | Debug console | interfaces |

### Input (src/input/)

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `manager.py` | Input handling, action mapping | pygame, bindings, actions |
| `bindings.py` | Key to action mapping | pygame, actions |
| `actions.py` | InputAction enum | none |

---

## Design Patterns

| Pattern | Implementation |
|---------|---------------|
| **Facade** | `Game` (main), `GameEngine` |
| **Observer** | `EventSystem` notifies listeners |
| **Factory** | `EntityFactory` creates entities |
| **ECS** | Entity-Component-System architecture |
| **Interface** | `IPhysics`, `IUIComponent`, `IUIManager` |

---

## API Reference

### GameEngine

```python
from engine.game_engine import GameEngine

class GameEngine:
    """
    Core game engine coordinating all game systems.
    
    The GameEngine is the main entry point for game logic, managing
    the update loop, systems coordination, and raycasting for rendering.
    
    Attributes:
        screen: Pygame surface for rendering
        state: Current GameState instance
        event_system: Event dispatcher for game events
        physics: Physics implementation for collision/LOS
        system_registry: Registry of all game systems
        dt: Current delta time
        running: Whether the game is running
        paused: Whether the game is paused
    
    Example:
        >>> engine = GameEngine(screen)
        >>> engine.start_game()
        >>> while engine.running:
        ...     engine.update(1/60)
        ...     # render
    """
    
    def __init__(self, screen: pygame.Surface) -> None:
        """
        Initialize the game engine.
        
        Args:
            screen: Pygame surface for rendering
            
        Raises:
            RuntimeError: If pygame not initialized
        """
        
    def start_game(self) -> None:
        """
        Start a new game.
        
        Initializes game state, loads map, emits GAME_START event.
        """
        
    def pause_game(self) -> None:
        """
        Pause the game.
        
        Sets game_state to "pause" if currently playing.
        """
        
    def resume_game(self) -> None:
        """
        Resume the game.
        
        Sets game_state to "playing" if currently paused.
        """
        
    def update(self, dt: float) -> None:
        """
        Update game state for one frame.
        
        Args:
            dt: Delta time in seconds since last update
        """
        
    def attack(self) -> None:
        """
        Player performs an attack through combat system.
        """
        
    def get_state(self) -> Dict[str, Any]:
        """
        Get current game state for serialization.
        
        Returns:
            Dictionary representation of game state
        """
        
    def get_ray_data(self) -> List[float]:
        """
        Get wall distances for raycasting.
        
        Returns:
            List of distances for each ray
        """
```

### SystemRegistry

```python
from engine.system_registry import SystemRegistry

class SystemRegistry:
    """
    Registry that holds and coordinates all game systems.
    
    The SystemRegistry is responsible for:
    - Registering and retrieving systems
    - Initializing systems with required dependencies
    - Updating all systems in the game loop
    
    Attributes:
        player_system: System handling player movement and input
        enemy_ai_system: System handling enemy AI behaviors
        combat_system: System handling combat mechanics
        physics: Physics instance for collision and raycasting
    
    Example:
        >>> registry = SystemRegistry()
        >>> registry.initialize(game_state, physics, input_manager)
        >>> registry.update_all(0.016)  # 60 FPS
    """
    
    def __init__(self) -> None:
        """Initialize the system registry."""
        
    def initialize(
        self, 
        state: GameState, 
        physics: Physics, 
        input_manager: Optional[InputManager] = None
    ) -> None:
        """
        Initialize all systems with required dependencies.
        
        Args:
            state: GameState instance
            physics: Physics instance for collision detection
            input_manager: Optional InputManager instance
        """
        
    def set_input_manager(self, input_manager: InputManager) -> None:
        """
        Set the input manager after initialization.
        
        Args:
            input_manager: InputManager instance to use
        """
        
    def register(self, name: str, system: ISystem) -> None:
        """
        Register a system with the registry.
        
        Args:
            name: Name to register the system under
            system: System instance to register
        """
        
    def get(self, name: str) -> Optional[ISystem]:
        """
        Get a system by name.
        
        Args:
            name: Name of the system to retrieve
            
        Returns:
            The system if found, None otherwise
        """
        
    def update_all(self, dt: float) -> None:
        """
        Update all registered systems.
        
        Systems are updated in registration order.
        
        Args:
            dt: Delta time since last update in seconds
        """
        
    def get_player_system(self) -> PlayerSystem:
        """Get the player system."""
        
    def get_enemy_ai_system(self) -> EnemyAISystem:
        """Get the enemy AI system."""
        
    def get_combat_system(self) -> CombatSystem:
        """Get the combat system."""
        
    def get_physics(self) -> Physics:
        """Get the physics instance."""
        
    def get_input_manager(self) -> Optional[InputManager]:
        """Get the input manager instance."""
```

### Entity Classes

```python
from entities.base import Entity, Component

class Component(ABC):
    """Base class for all entity components."""
    
    @property
    def entity(self) -> Optional["Entity"]:
        """Get the entity this component belongs to."""
        
    @entity.setter
    def entity(self, value: "Entity") -> None:
        """Set the entity this component belongs to."""


class Entity(ABC):
    """
    Base class for all game entities.
    
    Entities are objects that have a unique identity and are composed
    of components.
    
    Attributes:
        id: Unique identifier for this entity
        components: Dictionary of components attached to this entity
    """
    
    def __init__(self, entity_id: str) -> None:
        """
        Initialize the entity.
        
        Args:
            entity_id: Unique identifier for this entity
        """
        
    def get_component(self, name: str) -> Optional[Component]:
        """Get a component by name."""
        
    def add_component(self, component: Component, name: str = None) -> None:
        """Add a component to this entity."""
        
    def remove_component(self, name: str) -> None:
        """Remove a component from this entity."""
        
    def has_component(self, name: str) -> bool:
        """Check if entity has a specific component."""
        
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the entity for one frame."""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization."""
```

### PlayerEntity

```python
from entities.player import PlayerEntity

class PlayerEntity(Entity):
    """
    Player entity with specialized components for gameplay.
    
    The player entity contains all components needed for player
    functionality including position, health, combat, and input.
    
    Properties:
        position: PositionComponent for location/orientation
        health_component: HealthComponent for health management
        combat: CombatComponent for combat mechanics
        input: PlayerInputComponent for input state
        x, y: Player position
        angle: Player facing angle
        health: Current health
        attack_cooldown: Current attack cooldown
    
    Example:
        >>> player = PlayerEntity("player")
        >>> player.x = 5.0
        >>> player.y = 3.0
        >>> player.attack()  # if combat.can_attack()
    """
    
    def __init__(self, entity_id: str = "player") -> None:
        """Initialize the player entity with default components."""
        
    def update(self, dt: float) -> None:
        """Update player entity (combat cooldown)."""
        
    def reset(self) -> None:
        """Reset player to default state."""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert player entity to dictionary."""
```

### EnemyEntity

```python
from entities.enemy import EnemyEntity

class EnemyEntity(Entity):
    """
    Enemy entity with specialized components for AI and combat.
    
    Properties:
        position: PositionComponent
        health_component: HealthComponent
        ai: AIComponent for behavior
        combat: CombatComponent
        x, y, angle: Position and facing
        health: Current health
        state: AI state (patrol, chase, attack, dying, dead)
        patrol_dir: Direction for patrolling
        attack_cooldown: Time until next attack
        dying_progress: Death animation progress
        enemy_type: Type of enemy (imp, demon, cacodemon)
    
    Example:
        >>> enemy = EnemyEntity("enemy_0", "imp", 5.0, 3.0)
        >>> if enemy.state == "patrol":
        ...     enemy.move_forward()
    """
    
    def __init__(
        self, 
        entity_id: str, 
        enemy_type: str = "imp", 
        x: float = 0.0, 
        y: float = 0.0
    ) -> None:
        """
        Initialize the enemy entity.
        
        Args:
            entity_id: Unique identifier for this enemy
            enemy_type: Type of enemy (imp, demon, cacodemon, etc.)
            x: Starting X position
            y: Starting Y position
        """
        
    def update(self, dt: float) -> None:
        """Update enemy entity (AI cooldown)."""
```

### Component Classes

```python
from entities.components import (
    PositionComponent,
    HealthComponent,
    AIComponent,
    CombatComponent,
    PlayerInputComponent,
    CollidableComponent,
)

class PositionComponent(Component):
    """
    Component for entity position and orientation.
    
    Attributes:
        x: X coordinate position
        y: Y coordinate position
        angle: Facing angle in radians
    
    Methods:
        move(dx, dy): Move by delta
        rotate(da): Rotate by angle delta
        get_position(): Get (x, y) tuple
        get_direction(): Get direction vector from angle
        distance_to(x, y): Calculate distance to point
    """
    
    def __init__(self, x: float = 0.0, y: float = 0.0, angle: float = 0.0):
        """Initialize position component."""
    

class HealthComponent(Component):
    """
    Component for entity health and damage handling.
    
    Attributes:
        health: Current health points
        max_health: Maximum health points
        is_dead: Whether the entity is dead
    
    Methods:
        take_damage(amount): Apply damage, returns True if died
        heal(amount): Heal by amount
        health_percentage: Property for health as 0.0-1.0
    """
    
    def __init__(self, health: int = 100, max_health: int = 100):
        """Initialize health component."""
    

class AIComponent(Component):
    """
    Component for enemy AI behavior.
    
    Attributes:
        enemy_type: Type of enemy (imp, demon, etc.)
        state: Current AI state
        target: Target entity ID to track
        patrol_dir: Direction for patrolling in radians
        attack_cooldown: Time until next attack possible
        dying_progress: Progress of death animation (0.0 to 1.0)
    
    Methods:
        update_cooldown(dt): Update attack cooldown
        can_attack(): Check if can attack
    """
    

class CombatComponent(Component):
    """
    Component for combat mechanics.
    
    Attributes:
        attack_cooldown: Time until next attack possible
        attack_range: Maximum range for attacks
        attack_damage: Damage dealt per attack
    
    Methods:
        can_attack(): Check if attack ready
        perform_attack(): Consume cooldown, return success
        update(dt): Update cooldown timer
    """
```

### IPhysics Interface

```python
from physics.interfaces import IPhysics

class IPhysics(ABC):
    """
    Abstract interface for physics implementations.
    
    Implementations:
        - Physics: Standard raycast-based physics
        - Future: AStarPhysics for pathfinding-based movement
    
    Methods:
        is_wall(x, y) -> bool: Check if position contains wall
        has_line_of_sight(x1, y1, x2, y2) -> bool: Check LOS between points
        cast_ray(ray_angle, player_x, player_y) -> Dict: Cast ray, get collision
        check_collision(x, y) -> bool: Check wall collision at position
    """
    
    @abstractmethod
    def is_wall(self, x: float, y: float) -> bool:
        """Check if a position contains a wall."""
        
    @abstractmethod
    def has_line_of_sight(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> bool:
        """Check if there's a clear line of sight between two points."""
        
    @abstractmethod
    def cast_ray(
        self, ray_angle: float, player_x: float, player_y: float
    ) -> Dict[str, Any]:
        """
        Cast a ray from a point and return collision information.
        
        Returns:
            Dict with: dist (distance), side (wall side 0/1)
        """
        
    @abstractmethod
    def check_collision(self, x: float, y: float) -> bool:
        """Check if a position collides with any wall."""
```

### IUIComponent Interface

```python
from ui.interfaces import IUIComponent

class IUIComponent(ABC):
    """
    Base interface for all UI components.
    
    All UI components (Menu, HUD, Console) must implement this interface
    to be managed by the UIManager.
    
    Properties:
        active: Whether the component is currently visible
    
    Methods:
        update(dt): Update component state
        render(surface): Render to pygame surface
        handle_input(event): Handle input, return if handled
        show(): Make component visible
        hide(): Make component invisible
    """
    
    @property
    @abstractmethod
    def active(self) -> bool:
        """Check if the component is currently active (visible)."""
        
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the component's internal state."""
        
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render the component to the given surface."""
        
    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        
    @abstractmethod
    def show(self) -> None:
        """Show the component, making it visible and active."""
        
    @abstractmethod
    def hide(self) -> None:
        """Hide the component, making it invisible and inactive."""
```

### IUIManager Interface

```python
from ui.interfaces import IUIManager

class IUIManager(ABC):
    """
    Interface for UI management.
    
    The UIManager coordinates all UI components, handling registration,
    activation, updates, and rendering.
    
    Properties:
        active_component: Name of currently active UI component
    
    Methods:
        register(name, component): Register a UI component
        get(name): Get component by name
        set_active(name): Set active component
        update(dt): Update active component
        render(surface): Render active component
        handle_input(event): Forward input to active component
    """
    
    @property
    @abstractmethod
    def active_component(self) -> Optional[str]:
        """Get the name of the currently active component."""
        
    @abstractmethod
    def register(self, name: str, component: IUIComponent) -> None:
        """Register a UI component with the manager."""
        
    @abstractmethod
    def get(self, name: str) -> Optional[IUIComponent]:
        """Get a registered component by name."""
        
    @abstractmethod
    def set_active(self, name: str) -> None:
        """Set the active component by name."""
        
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update all active components."""
        
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render all active components."""
        
    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Forward input to the active component."""
```

### UIManager

```python
from ui.manager import UIManager

class UIManager(IUIManager):
    """
    Manages UI components in the game.
    
    The UIManager maintains a registry of UI components and controls
    which components are active at any time. Only the active component
    receives update and render calls.
    
    Additional Methods:
        show_component(name): Explicitly show component (for overlays)
        hide_component(name): Explicitly hide component
        clear(): Remove all components
    
    Example:
        >>> manager = UIManager()
        >>> manager.register("menu", main_menu)
        >>> manager.register("hud", hud)
        >>> manager.set_active("menu")
        >>> # Now only menu will update and render
    """
    
    def __init__(self) -> None:
        """Initialize the UI manager with an empty component registry."""
```

### InputManager

```python
from input.manager import InputManager

class InputManager:
    """
    Manages player input from keyboard and mouse.
    
    Provides:
    - Key state tracking (pressed/held)
    - Action-based input lookup via InputAction enum
    - Mouse position and button tracking
    - Backward compatibility with original InputHandler
    
    Example:
        >>> input_mgr = InputManager()
        >>> input_mgr.update()
        >>> actions = input_mgr.get_pressed_actions()
        >>> if InputAction.MOVE_FORWARD in actions:
        ...     print("Moving forward!")
    """
    
    def __init__(self) -> None:
        """Initialize the input manager."""
        
    def update(self) -> None:
        """Update input state from pygame (call each frame)."""
        
    def get_pressed_actions(self) -> Set[InputAction]:
        """Get all currently pressed actions."""
        
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if a specific action is currently pressed."""
        
    def get_keys(self) -> Dict[str, bool]:
        """Get current key states (legacy compatibility)."""
        
    def is_key_pressed(self, key: str) -> bool:
        """Check if a specific key is pressed (legacy)."""
        
    def get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is pressed."""
        
    def get_binding_map(self) -> KeyBindingMap:
        """Get the key binding map."""
```

### InputAction Enum

```python
from input.actions import InputAction

class InputAction(str, Enum):
    """
    Enum representing all possible player input actions.
    
    Movement:
        MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT
    
    Rotation:
        ROTATE_LEFT, ROTATE_RIGHT
    
    Game actions:
        ATTACK, PAUSE, CONSOLE, QUIT
    
    Example:
        >>> if InputAction.ATTACK in input_mgr.get_pressed_actions():
        ...     engine.attack()
    """
    
    # Movement
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    
    # Rotation
    ROTATE_LEFT = "rotate_left"
    ROTATE_RIGHT = "rotate_right"
    
    # Game actions
    ATTACK = "attack"
    PAUSE = "pause"
    CONSOLE = "console"
    QUIT = "quit"
```

### KeyBindingMap

```python
from input.bindings import KeyBindingMap

class KeyBindingMap:
    """
    Maps pygame key constants to InputAction values.
    
    Example:
        >>> binding_map = KeyBindingMap()
        >>> action = binding_map.get_action(pygame.K_w)
        >>> print(action)
        InputAction.MOVE_FORWARD
        
        # Custom binding
        >>> binding_map.register(pygame.K_UP, InputAction.MOVE_FORWARD)
    """
    
    def __init__(self) -> None:
        """Initialize the binding map with default WebDoom bindings."""
        
    def register(self, key: int, action: InputAction) -> None:
        """Register a key binding."""
        
    def unregister(self, key: int) -> None:
        """Remove a key binding."""
        
    def get_action(self, key: int) -> Optional[InputAction]:
        """Get the action associated with a key."""
        
    def get_key(self, action: InputAction) -> Optional[int]:
        """Get the key bound to an action."""
        
    def get_bound_keys(self) -> Set[int]:
        """Get all currently bound keys."""
        
    def get_all_bindings(self) -> Dict[int, InputAction]:
        """Get a copy of all bindings."""
        
    def clear(self) -> None:
        """Clear all key bindings."""
        
    def reset_to_defaults(self) -> None:
        """Reset all bindings to WebDoom defaults."""
```

### EntityFactory

```python
from entities.factory import EntityFactory

class EntityFactory:
    """
    Factory for creating game entities.
    
    Example:
        >>> factory = EntityFactory()
        >>> player = factory.create_player("player")
        >>> enemy = factory.create_enemy("imp", 5.0, 3.0)
        >>> enemies = factory.create_enemies_from_map(map_data)
    """
    
    # Mapping from map characters to enemy types
    ENEMY_TYPE_MAP = {
        "E": "imp",
        "D": "demon",
        "C": "cacodemon",
    }
    
    def __init__(self) -> None:
        """Initialize the entity factory."""
        
    def create_player(self, entity_id: str = "player") -> PlayerEntity:
        """Create a player entity."""
        
    def create_enemy(
        self, 
        enemy_type: str, 
        x: float, 
        y: float, 
        entity_id: str = None
    ) -> EnemyEntity:
        """Create an enemy entity."""
        
    def create_enemies_from_map(self, map_data: List[str]) -> List[EnemyEntity]:
        """Create enemy entities from map data."""
        
    def create_enemy_at_position(
        self, char: str, x: float, y: float
    ) -> Optional[EnemyEntity]:
        """Create an enemy at a specific position based on map character."""
        
    def reset(self) -> None:
        """Reset the entity counter."""
```

---

## Usage Examples

### Creating Entities

```python
from entities.player import PlayerEntity
from entities.enemy import EnemyEntity
from entities.components import PositionComponent, HealthComponent

# Create a player
player = PlayerEntity("player")
player.x = 1.5
player.y = 1.5
player.angle = 0.0

# Access components
position = player.position  # PositionComponent
health = player.health_component  # HealthComponent

# Create an enemy
enemy = EnemyEntity("enemy_0", "imp", 5.0, 3.0)
print(f"Enemy type: {enemy.enemy_type}")
print(f"Enemy health: {enemy.health}")

# Add custom components
enemy.add_component(PositionComponent(10.0, 10.0, 1.57))
```

### Registering Systems

```python
from engine.game_engine import GameEngine
from engine.system_registry import SystemRegistry
from physics.physics import Physics

# GameEngine already creates a SystemRegistry internally
engine = GameEngine(screen)

# Access systems through registry
player_system = engine.system_registry.get_player_system()
enemy_ai_system = engine.system_registry.get_enemy_ai_system()
combat_system = engine.system_registry.get_combat_system()

# Update all systems manually (GameEngine does this automatically)
engine.system_registry.update_all(0.016)  # 60 FPS = 0.016s per frame
```

### Using UI Manager

```python
from ui.manager import UIManager
from ui.menu import Menu
from ui.hud import HUD
from ui.console import Console

# Create manager
ui_manager = UIManager()

# Register components
ui_manager.register("main_menu", Menu(screen))
ui_manager.register("hud", HUD(screen))
ui_manager.register("console", Console(screen))

# Switch active component
ui_manager.set_active("main_menu")

# In game loop - update and render only active component
ui_manager.update(dt)
ui_manager.render(screen)

# Handle input - forwards to active component
for event in pygame.event.get():
    if ui_manager.handle_input(event):
        continue  # Event handled by UI
```

### Using Input System

```python
from input.manager import InputManager
from input.actions import InputAction

# Create input manager
input_manager = InputManager()

# In game loop
input_manager.update()

# Check actions
actions = input_manager.get_pressed_actions()

if InputAction.MOVE_FORWARD in actions:
    player.move_forward()

if InputAction.ATTACK in actions:
    player.attack()

if InputAction.ROTATE_LEFT in actions:
    player.rotate(-rotation_speed * dt)

# Legacy key support still works
keys = input_manager.get_keys()
if keys.get("KeyW"):
    player.move_forward()

# Check specific keys
if input_manager.is_key_pressed("Space"):
    player.attack()
```

### Using Physics Interface

```python
from physics.physics import Physics

# Create physics instance
physics = Physics()

# Set map grid
physics.set_map(map_grid)

# Check if position is a wall
if physics.is_wall(player.x + dx, player.y + dy):
    # Cannot move here
    pass

# Check line of sight
if physics.has_line_of_sight(player.x, player.y, enemy.x, enemy.y):
    # Enemy is visible
    enemy.set_state("chase")

# Cast ray for rendering
ray_result = physics.cast_ray(angle, player.x, player.y)
distance = ray_result["dist"]
side = ray_result["side"]

# Check collision
if physics.check_collision(new_x, new_y):
    # Collision with wall
    pass
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

---

## Backward Compatibility Notes

### InputHandler
The original `InputHandler` class is preserved as an alias to `InputManager` for backward compatibility:

```python
from input.manager import InputHandler  # Same as InputManager

handler = InputHandler()
# Works exactly like InputManager
```

### Key Names
Legacy key names are still supported in `get_keys()`:
- `KeyW`, `KeyS`, `KeyA`, `KeyD`
- `ArrowLeft`, `ArrowRight`
- `Space`, `Escape`

---

## Class Hierarchy

```
Component (ABC)
├── PositionComponent
├── HealthComponent
├── AIComponent
├── CombatComponent
├── PlayerInputComponent
└── CollidableComponent

Entity (ABC)
├── PlayerEntity
└── EnemyEntity

IUIComponent (ABC)
├── Menu
├── HUD
└── Console

IUIManager (ABC)
└── UIManager

IPhysics (ABC)
└── Physics

ISystem (ABC)
├── PlayerSystem
├── EnemyAISystem
└── CombatSystem
```