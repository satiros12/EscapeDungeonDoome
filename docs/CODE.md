# WebDoom Code Documentation

This document provides a comprehensive overview of the WebDoom codebase, explaining how the code is organized and what each file and class contains.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Entry Point](#entry-point)
3. [Core Modules](#core-modules)
4. [Engine](#engine)
5. [Systems](#systems)
6. [Entities](#entities)
7. [Physics](#physics)
8. [Input](#input)
9. [UI](#ui)
10. [Renderer](#renderer)

---

## Project Structure

```
src/
├── main.py              # Entry point
├── game.py              # Main game facade
├── config.py            # Configuration constants
├── renderer.py          # Rendering engine
│
├── engine/              # Core game engine
│   ├── game_engine.py   # Main game engine
│   ├── game_state.py    # Game state management
│   ├── event_system.py  # Event dispatcher
│   └── system_registry.py # System coordination
│
├── systems/             # Game systems (ECS pattern)
│   ├── base.py          # System base classes
│   ├── player_system.py # Player movement
│   ├── enemy_ai_system.py # Enemy AI
│   └── combat_system.py # Combat mechanics
│
├── entities/            # Entity-Component system
│   ├── base.py          # Entity/Component bases
│   ├── components.py    # Component classes
│   ├── player.py        # Player entity
│   ├── enemy.py         # Enemy entity
│   └── factory.py       # Entity factory
│
├── physics/             # Physics engine
│   ├── physics.py       # Physics implementation
│   └── interfaces.py    # Physics interfaces
│
├── input/               # Input handling
│   ├── actions.py       # Input actions enum
│   ├── bindings.py      # Key bindings
│   └── manager.py       # Input manager
│
└── ui/                  # User interface
    ├── interfaces.py    # UI interfaces
    ├── manager.py       # UI manager
    ├── menu.py          # Menu system
    ├── hud.py           # Heads-up display
    └── console.py       # Debug console
```

---

## Entry Point

### `src/main.py`

**Purpose**: Application entry point that initializes pygame and starts the game.

**Key Functions**:
- `main()` - Initializes pygame, creates Game instance, and runs the game loop

**Usage**:
```bash
python src/main.py
```

---

## Core Modules

### `src/config.py`

**Purpose**: Central configuration file containing all game constants.

**Constants**:
| Category | Constants |
|----------|-----------|
| Screen | `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS` |
| Colors | `COLOR_BLACK`, `COLOR_WHITE`, `COLOR_RED`, etc. |
| Player | `PLAYER_SPEED`, `PLAYER_ROTATION_SPEED`, `PLAYER_START_HEALTH` |
| Enemy | `ENEMY_COUNT`, `ENEMY_HEALTH`, `ENEMY_SPEED` |
| Combat | `ATTACK_DAMAGE`, `ATTACK_RANGE`, `ATTACK_COOLDOWN` |
| Raycasting | `FOV`, `RAY_COUNT`, `MAX_DEPTH` |
| Map | `TILE_SIZE` |
| UI | `HUD_HEIGHT`, `HUD_COLOR`, `FONT_SIZE` |

---

### `src/game.py`

**Purpose**: Main game facade that coordinates all game components. Acts as the top-level coordinator between rendering, input, engine, and UI.

**Class**: `Game`

**Key Attributes**:
- `screen` - Pygame display surface
- `clock` - Frame rate control
- `input_handler` - Input management
- `renderer` - Rendering engine
- `game_engine` - Core game logic
- `ui_manager` - UI component management
- `current_map` - Active map name

**Key Methods**:
- `__init__()` - Initialize all game components
- `_setup_ui()` - Create and register UI components
- `_create_menus()` - Create main and options menus
- `run()` - Main game loop
- `_handle_events()` - Process pygame events
- `_update(dt)` - Update game state
- `_render()` - Render current frame

**Game States**: `menu`, `playing`, `pause`, `victory`, `defeat`

---

### `src/renderer.py`

**Purpose**: Handles all rendering operations using Pygame, including raycasting walls, sprites, and UI overlays.

**Class**: `Renderer`

**Key Methods**:
- `set_physics(physics)` - Connect physics for line-of-sight checks
- `clear(color)` - Clear screen
- `present()` - Flip display buffer
- `render_floor_ceiling()` - Draw floor and ceiling
- `render_walls_raycasted(player, wall_distances, map_data)` - Render 3D walls
- `render_enemies(player, enemies, map_data)` - Render enemy sprites
- `render_crosshair()` - Draw center crosshair
- `render_lighting(player)` - Apply lighting effects (vignette, torch)
- `render_text(text, x, y, color, size)` - Render text

**Features**:
- Pre-rendered textures for performance
- Distance-based shading
- Sprite scaling based on distance
- Lighting effects (vignette, torch flicker)

---

## Engine

### `src/engine/game_engine.py`

**Purpose**: Core game engine that coordinates all game systems using the ECS (Entity-Component-System) pattern.

**Class**: `GameEngine`

**Key Attributes**:
- `screen` - Pygame surface
- `state` - GameState instance
- `event_system` - Event dispatcher
- `physics` - Physics engine (IPhysics)
- `system_registry` - System coordinator
- `ray_angles` - Pre-computed ray angles
- `wall_distances` - Current wall distances for rendering

**Key Methods**:
- `start_game()` - Initialize new game, parse map
- `pause_game()` - Pause the game
- `resume_game()` - Resume from pause
- `update(dt)` - Update all systems for one frame
- `_cast_rays()` - Cast rays for raycasting rendering
- `get_ray_data()` - Get wall distances for renderer
- `attack()` - Trigger player attack

**Integration**:
- Uses `SystemRegistry` to coordinate `PlayerSystem`, `EnemyAISystem`, and `CombatSystem`
- Handles raycasting for the renderer
- Emits game events via `EventSystem`

---

### `src/engine/game_state.py`

**Purpose**: Manages all game state data including player, enemies, maps, and items.

**Classes**:

#### `MapManager`
Manages map data and loading.

**Key Methods**:
- `get_current_map()` - Get active map data
- `set_map(map_name)` - Change active map
- `get_available_maps()` - List available maps

#### `ItemType`
Constants for item types:
- `HEALTH_PACK`, `AMMO_SHOTGUN`, `AMMO_CHAINGUN`
- `WEAPON_FISTS`, `WEAPON_SWORD`, `WEAPON_AXE`
- `ARMOR_LIGHT`, `ARMOR_HEAVY`

#### `Item` (dataclass)
Represents a collectible item.

**Attributes**: `x`, `y`, `item_type`, `value`, `collected`

#### `Player` (dataclass)
Represents the player entity.

**Attributes**: `x`, `y`, `angle`, `health`, `attack_cooldown`, `god_mode`, `speed_multiplier`, `current_weapon`, `ammo`, `armor`, `armor_type`

#### `EnemyType`
Constants for enemy types:
- `IMP`, `DEMON`, `CACODEMON`
- `SOLDIER_PISTOL`, `SOLDIER_SHOTGUN`, `CHAINGUNNER`

#### `Enemy` (dataclass)
Represents an enemy entity.

**Attributes**: `x`, `y`, `angle`, `health`, `state`, `patrol_dir`, `attack_cooldown`, `dying_progress`, `enemy_type`, `weapon`, `armor`, `armor_type`

**Enemy States**: `patrol`, `searching`, `chase`, `attack`, `dying`, `dead`

#### `Corpse` (dataclass)
Represents a dead enemy.

**Attributes**: `x`, `y`

#### `HitEffect` (dataclass)
Represents a visual hit effect.

**Attributes**: `x`, `y`, `timer`

#### `GameState`
Main game state container.

**Key Attributes**:
- `game_state` - Current game state string
- `player` - Player instance
- `enemies` - List of Enemy instances
- `corpses` - List of dead enemies
- `kills` - Kill counter
- `hit_effects` - Active hit effects
- `pending_input` - Input buffer
- `map_manager` - Map management

**Key Methods**:
- `parse_map(map_data)` - Parse map and spawn entities
- `reset()` - Reset to initial state

---

### `src/engine/event_system.py`

**Purpose**: Event dispatcher for game events using the Observer pattern.

**Classes**:

#### `EventType`
Enum of game event types:
- `GAME_START`, `GAME_WIN`, `GAME_OVER`, `PLAYER_DEATH`
- `PLAYER_DAMAGE`, `ENEMY_DEATH`, `ENEMY_HIT`
- `WEAPON_FIRE`, `WEAPON_HIT`, `ITEM_PICKUP`

#### `EventSystem`
Event dispatcher.

**Key Methods**:
- `subscribe(event_type, callback)` - Register event listener
- `unsubscribe(event_type, callback)` - Remove event listener
- `emit(event_type, data)` - Emit an event
- `process_events()` - Process queued events

---

### `src/engine/system_registry.py`

**Purpose**: Coordinates all game systems in the ECS architecture.

**Class**: `SystemRegistry`

**Key Attributes**:
- `player_system` - Player movement system
- `enemy_ai_system` - Enemy AI system
- `combat_system` - Combat system

**Key Methods**:
- `initialize(state, physics)` - Initialize all systems with dependencies
- `update_all(dt)` - Update all systems in order
- `get_player_system()` - Get player system
- `get_enemy_ai_system()` - Get enemy AI system
- `get_combat_system()` - Get combat system

---

## Systems

The systems implement the ECS (Entity-Component-System) pattern, handling specific game logic domains.

### `src/systems/base.py`

**Purpose**: Base classes for all game systems.

**Classes**:

#### `GameEvent` (dataclass)
Represents a game event.

**Attributes**: `type` (str), `data` (Dict)

#### `ISystem` (ABC)
Interface for all game systems.

**Methods**:
- `update(dt)` - Update system state
- `on_event(event)` - Handle game events

#### `SystemBase`
Base implementation with common functionality.

**Methods**:
- `update(dt)` - Abstract update method
- `on_event(event)` - Append event to queue
- `clear_events()` - Clear event queue

---

### `src/systems/player_system.py`

**Purpose**: Handles player movement and input processing.

**Class**: `PlayerSystem(SystemBase)`

**Key Methods**:
- `update(dt)` - Process player movement based on input
- Handles forward/backward movement, strafing, rotation
- Applies collision detection via physics

**Dependencies**: `GameState`, `Physics`

---

### `src/systems/enemy_ai_system.py`

**Purpose**: Handles enemy AI behaviors and state transitions.

**Class**: `EnemyAISystem(SystemBase)`

**AI Configuration**:
- `detection_range = 10.0` - Distance to detect player
- `attack_range = 1.0` - Distance to attack
- `enemy_speed = 2.5` - Movement speed
- `patrol_speed = 1.0` - Patrol movement speed
- `lost_player_distance = 12.0` - Distance to lose player

**Key Methods**:
- `update(dt)` - Update all enemies
- `_update_enemy(enemy, player, dt)` - Update single enemy
- `_update_patrol(enemy, dt, can_see, dist)` - Patrol behavior
- `_update_chase(enemy, player, dist, angle, dt, can_see)` - Chase behavior
- `_update_attack(enemy, player, dist, dt)` - Attack behavior
- `normalize_angle(angle)` - Keep angle in [-PI, PI]

**Enemy State Machine**: `patrol` → `chase` → `attack`

---

### `src/systems/combat_system.py`

**Purpose**: Handles combat mechanics, damage, and win conditions.

**Class**: `CombatSystem(SystemBase)`

**Combat Configuration**:
- `attack_range = 1.5` - Player attack range
- `attack_damage = 10` - Damage per hit
- `attack_cooldown = 0.5` - Seconds between attacks

**Key Methods**:
- `update(dt)` - Update combat state
- `player_attack()` - Process player attack on nearby enemies
- `_update_dying_enemies(dt)` - Handle dying animation
- `_update_hit_effects(dt)` - Clean up expired effects
- `_check_win_condition()` - Check if all enemies dead

---

## Entities

The entity system implements the Entity-Component pattern for flexible game object composition.

### `src/entities/base.py`

**Purpose**: Base classes for Entity-Component architecture.

**Classes**:

#### `Component` (ABC)
Base class for all components.

**Methods**:
- `update(dt)` - Update component state

#### `Entity` (ABC)
Base class for all entities.

**Key Attributes**:
- `id` - Unique identifier
- `components` - Dict of attached components

**Key Methods**:
- `get_component(name)` - Get component by name
- `add_component(component)` - Attach component
- `remove_component(name)` - Detach component
- `update(dt)` - Update entity and all components

---

### `src/entities/components.py`

**Purpose**: Concrete component implementations.

**Classes**:

#### `PositionComponent`
Manages entity position and rotation.

**Attributes**: `x`, `y`, `angle`

**Methods**:
- `move(dx, dy)` - Move by delta
- `rotate(da)` - Rotate by delta
- `get_position()` - Returns (x, y) tuple

#### `HealthComponent`
Manages entity health.

**Attributes**: `health`, `max_health`

**Methods**:
- `take_damage(amount)` - Reduce health
- `heal(amount)` - Increase health
- `is_alive()` - Check if health > 0

#### `AIComponent`
Manages enemy AI state.

**Attributes**: `enemy_type`, `state`, `target`

#### `CombatComponent`
Manages combat properties.

**Attributes**: `attack_cooldown`, `attack_range`, `attack_damage`

#### `PlayerInputComponent`
Manages player input state.

**Attributes**: `pending_actions` - Set of input actions

#### `CollidableComponent`
Manages collision properties.

**Attributes**: `collision_radius`, `on_collision` callback

---

### `src/entities/player.py`

**Purpose**: Player entity implementation.

**Class**: `PlayerEntity(Entity)`

**Components**:
- `PositionComponent` - Position and angle
- `HealthComponent` - Health management
- `CombatComponent` - Attack properties
- `PlayerInputComponent` - Input handling

---

### `src/entities/enemy.py`

**Purpose**: Enemy entity implementation.

**Class**: `EnemyEntity(Entity)`

**Enemy Types**:
- `IMP` - Basic enemy (30 HP, fast)
- `DEMON` - Medium enemy (60 HP)
- `CACODEMON` - Boss enemy (100 HP, slow)

**Components**:
- `PositionComponent` - Position and angle
- `HealthComponent` - Health management
- `AIComponent` - AI state
- `CombatComponent` - Attack properties
- `CollidableComponent` - Collision radius

---

### `src/entities/factory.py`

**Purpose**: Factory for creating entities from map data.

**Class**: `EntityFactory`

**Key Methods**:
- `create_player(entity_id)` - Create player entity
- `create_enemy(entity_id, enemy_type, x, y)` - Create enemy entity
- `create_enemies_from_map(map_data)` - Parse map and create enemies

---

## Physics

### `src/physics/interfaces.py`

**Purpose**: Abstract interfaces for physics implementation.

**Classes**:

#### `IPhysics` (ABC)
Interface for physics engine.

**Methods**:
- `is_wall(x, y)` - Check if position is a wall
- `has_line_of_sight(x1, y1, x2, y2)` - Check visibility
- `cast_ray(ray_angle, player_x, player_y)` - Cast single ray
- `check_collision(x, y)` - Check collision with margin

---

### `src/physics/physics.py`

**Purpose**: Physics implementation for collision and raycasting.

**Class**: `Physics(IPhysics)`

**Key Attributes**:
- `ray_step = 0.02` - Ray marching step size
- `max_depth = 20.0` - Maximum ray distance
- `collision_margin = 0.35` - Collision buffer

**Key Methods**:
- `set_map(grid)` - Set map grid for physics
- `get_map()` - Get current map grid
- `is_wall(x, y)` - Check wall at position
- `has_line_of_sight(x1, y1, x2, y2)` - Check visibility
- `cast_ray(ray_angle, x, y)` - Cast ray, returns dict with `dist` and `side`
- `check_collision(x, y)` - Check with collision margin
- `distance_to_wall(x, y, angle)` - Distance to nearest wall
- `get_wall_normal(x, y)` - Get wall surface normal

---

## Input

### `src/input/actions.py`

**Purpose**: Input action definitions.

**Class**: `InputAction` (StrEnum)

**Actions**:
- Movement: `MOVE_FORWARD`, `MOVE_BACKWARD`, `MOVE_LEFT`, `MOVE_RIGHT`
- Rotation: `ROTATE_LEFT`, `ROTATE_RIGHT`
- Game: `ATTACK`, `PAUSE`, `CONSOLE`, `QUIT`

---

### `src/input/bindings.py`

**Purpose**: Maps pygame keys to input actions.

**Class**: `KeyBindingMap`

**Default Bindings**:
| Key | Action |
|-----|--------|
| W | MOVE_FORWARD |
| S | MOVE_BACKWARD |
| A | MOVE_LEFT |
| D | MOVE_RIGHT |
| ← | ROTATE_LEFT |
| → | ROTATE_RIGHT |
| Space | ATTACK |
| ESC | PAUSE |
| P | CONSOLE |

**Key Methods**:
- `register(key, action)` - Add key binding
- `unregister(key)` - Remove binding
- `get_action(key)` - Get action for key
- `get_key(action)` - Get key for action
- `reset_to_defaults()` - Restore default bindings

---

### `src/input/manager.py`

**Purpose**: Central input management.

**Class**: `InputManager`

**Key Methods**:
- `update()` - Poll current key states
- `get_pressed_actions()` - Get set of currently pressed actions
- `is_action_pressed(action)` - Check specific action
- `get_keys()` - Get legacy key state dict (for backward compatibility)
- `is_key_pressed(key)` - Check legacy key state

**Also exports**: `InputHandler` as alias for backward compatibility

---

## UI

### `src/ui/interfaces.py`

**Purpose**: Abstract interfaces for UI components.

**Classes**:

#### `IUIComponent` (ABC)
Interface for all UI components.

**Properties**:
- `active` - Whether component is visible

**Methods**:
- `update(dt)` - Update component state
- `render(surface)` - Render to surface
- `handle_input(event)` - Handle input, returns bool
- `show()` - Make visible
- `hide()` - Make invisible

#### `IUIManager` (ABC)
Interface for UI management.

**Properties**:
- `active_component` - Currently active component name

**Methods**:
- `register(name, component)` - Register component
- `get(name)` - Get component by name
- `set_active(name)` - Activate component
- `update(dt)` - Update active component
- `render(surface)` - Render active component
- `handle_input(event)` - Forward input to active

---

### `src/ui/manager.py`

**Purpose**: Manages all UI components.

**Class**: `UIManager(IUIManager)`

**Key Methods**:
- `register(name, component)` - Register UI component
- `get(name)` - Get registered component
- `set_active(name)` - Set active component
- `show_component(name)` - Show specific component
- `hide_component(name)` - Hide specific component
- `update(dt)` - Update active component
- `render(surface)` - Render active component
- `handle_input(event)` - Forward to active component
- `clear()` - Unregister all components

---

### `src/ui/menu.py`

**Purpose**: Menu system for game navigation.

**Classes**:

#### `MenuItem` (dataclass)
Single menu item.

**Attributes**: `text`, `callback`, `selected`

#### `Menu` (IUIComponent)
Menu container.

**Key Methods**:
- `add_item(text, callback)` - Add menu item
- `handle_input(event)` - Handle navigation
- `update(dt)` - Update animations
- `render(surface)` - Render menu

**Navigation**: Arrow keys (up/down), Enter to select

#### `create_main_menu()` - Factory function for main menu
- "Start Game"
- "Options"
- "Quit"

#### `OptionsMenu(IUIComponent)`
Map selection menu.

**Key Methods**:
- `handle_input(event)` - Handle selection
- `render(surface)` - Render options

---

### `src/ui/hud.py`

**Purpose**: Heads-up display showing game information.

**Class**: `HUD(IUIComponent)`

**Key Methods**:
- `show()` / `hide()` - Visibility control
- `update(dt)` - Update state
- `render(surface)` - Render HUD
- `render_with_data(surface, health, kills, weapon)` - Render with data

**Display Elements**:
- Health bar with color gradient (green → yellow → red)
- Kill counter
- Current weapon

---

### `src/ui/console.py`

**Purpose**: Debug console for developers.

**Class**: `Console(IUIComponent)`

**Key Methods**:
- `toggle()` - Show/hide console
- `update(input_state)` - Process input
- `render(surface)` - Render console
- `handle_input(event)` - Handle commands

**Commands**:
- `help` - Show available commands
- `god` - Toggle god mode
- `killall` - Kill all enemies
- `map <name>` - Change map

**Toggle**: P key

---

## Usage Examples

### Creating a New Game

```python
import pygame
from game import Game

pygame.init()
game = Game()
game.run()
```

### Using the Physics System

```python
from physics import Physics

# Create physics with map grid
grid = ["####", "#  #", "####"]
physics = Physics(grid)

# Check walls
if physics.is_wall(5, 5):
    print("Wall detected")

# Check line of sight
if physics.has_line_of_sight(1, 1, 3, 3):
    print("Clear view")

# Cast ray
result = physics.cast_ray(math.pi / 4, 1, 1)
print(f"Wall at distance {result['dist']}")
```

### Using the Input System

```python
from input import InputManager, InputAction

input_mgr = InputManager()
input_mgr.update()

# Check actions
if input_mgr.is_action_pressed(InputAction.MOVE_FORWARD):
    print("Moving forward")

# Get all pressed actions
pressed = input_mgr.get_pressed_actions()
```

### Creating Entities

```python
from entities.factory import EntityFactory

factory = EntityFactory()

# Create player
player = factory.create_player("player_1")

# Create enemy
imp = factory.create_enemy("imp_1", "imp", 5, 5)

# Create from map
enemies = factory.create_enemies_from_map(map_grid)
```

---

## Testing

Run tests with pytest:

```bash
# All unit tests
python -m pytest tests/unit/ -v

# Specific test file
python -m pytest tests/unit/test_systems.py -v

# With coverage
python -m pytest tests/unit/ --cov=src
```

---

## Architecture Patterns

### Entity-Component-System (ECS)
- **Entities**: Game objects with unique IDs
- **Components**: Data containers attached to entities
- **Systems**: Logic processors that operate on entities with specific components

### Observer Pattern
- **EventSystem**: Dispatches events to registered callbacks
- Used for loose coupling between game systems

### Factory Pattern
- **EntityFactory**: Creates entities from map data
- **MapManager**: Loads and manages map data

### Interface Segregation
- **IPhysics**: Abstract physics implementation
- **IUIComponent**: Abstract UI component
- **IUIManager**: Abstract UI manager
- **ISystem**: Abstract system base

---

## Configuration

All game configuration is centralized in `config.py`. Key values:

| Setting | Default | Description |
|---------|---------|-------------|
| SCREEN_WIDTH | 800 | Window width |
| SCREEN_HEIGHT | 600 | Window height |
| FPS | 60 | Target frame rate |
| PLAYER_SPEED | 3.0 | Movement speed |
| FOV | 60 | Field of view (degrees) |
| RAY_COUNT | 800 | Number of rays for rendering |
| MAX_DEPTH | 20 | Maximum view distance |

---

*Last updated: 2026*