# WebDoom Component-Oriented Transformation Plan

## Executive Summary

This document outlines a comprehensive plan to transform WebDoom from its current hybrid architecture into a fully **Component-Oriented Design (COD)**. The goal is to achieve maximum modularity, reusability, and testability through a clean component-based architecture where all game objects are composed of reusable, composable components.

---

## Current Architecture Analysis

### What Already Exists

The codebase already has some component-oriented infrastructure:

1. **Entity Base Classes** (`src/entities/base.py`)
   - `Entity` base class with component management
   - `Component` base class with entity reference
   - Methods: `add_component()`, `get_component()`, `remove_component()`

2. **Component Classes** (`src/entities/components.py`)
   - `PositionComponent` - Position and rotation
   - `HealthComponent` - Health management
   - `AIComponent` - Enemy AI state
   - `CombatComponent` - Combat properties
   - `PlayerInputComponent` - Input state
   - `CollidableComponent` - Collision detection

3. **PlayerEntity and EnemyEntity** (`src/entities/player.py`, `enemy.py`)
   - Concrete entity implementations

4. **SystemRegistry** (`src/engine/system_registry.py`)
   - System coordination for ECS pattern

### Current Gaps and Problems

| Issue | Description | Impact |
|-------|-------------|--------|
| **Dual Data Structures** | GameState uses dataclasses (Player, Enemy) while entities exist but are unused | Code duplication, confusion |
| **No World/EntityManager** | No central entity container | Can't iterate entities by type |
| **Systems operate on dataclasses** | Systems read/write GameState.player/enemies directly | Not using the entity system |
| **No Component queries** | No way to query entities by component type | Limited flexibility |
| **Incomplete entity lifecycle** | No entity creation/destruction events | Memory management issues |
| **Mixed responsibilities** | Some logic in entities, some in GameState | Architecture not clean |

---

## Target Architecture

### High-Level Component-Oriented Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WORLD (Entity Manager)                            │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  EntityContainer                                                      │  │
│  │  - entities: Dict[str, Entity]                                       │  │
│  │  - component_queries: Dict[type, List[Entity]]                       │  │
│  │  - systems: List[System]                                             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│         ┌─────────────────────────┼─────────────────────────┐             │
│         ▼                         ▼                         ▼             │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│  │   Player    │          │   Enemies   │          │   Items     │        │
│  │  (Entity)   │          │  (Entities)  │          │  (Entities) │        │
│  │             │          │             │          │             │        │
│  │ Position    │          │ Position    │          │ Position   │        │
│  │ Health      │          │ Health      │          │ Item        │        │
│  │ Combat      │          │ AI          │          │ Collectible │        │
│  │ Input       │          │ Combat      │          └─────────────┘        │
│  └─────────────┘          │ Collidable  │                                  │
│                           └─────────────┘                                  │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     ▼
                    ┌────────────────────────────────┐
                    │         SYSTEMS                 │
                    │  ┌────────┐ ┌───────┐ ┌────┐  │
                    │  │ Player │ │  AI   │ │UI  │  │
                    │  │ System │ │System │ │    │  │
                    │  └────────┘ └───────┘ └────┘  │
                    └────────────────────────────────┘
```

### Component Categories

1. **Core Components** - Position, Rotation, Scale
2. **State Components** - Health, Stamina, Mana
3. **AI Components** - StateMachine, Target, Pathfinding
4. **Combat Components** - Weapon, Damage, Armor
5. **Input Components** - Keyboard, Gamepad
6. **Physics Components** - Collider, RigidBody, Trigger
7. **Render Components** - Sprite, Animation, Light
8. **Audio Components** - SoundSource, SoundListener

---

## Transformation Phases

### Phase 1: Entity Container and World (Week 1)

**Goal**: Create a central World class that manages all entities.

#### Task 1.1: Create World Class
```python
# src/world/world.py

class World:
    """Central entity container and system coordinator."""
    
    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._component_index: Dict[type, List[Entity]] = {}
        self._systems: List[ISystem] = []
    
    def create_entity(self, entity: Entity) -> None:
        """Register an entity in the world."""
        self._entities[entity.id] = entity
        self._index_entity(entity)
    
    def destroy_entity(self, entity_id: str) -> None:
        """Remove an entity from the world."""
        if entity_id in self._entities:
            entity = self._entities.pop(entity_id)
            self._unindex_entity(entity)
    
    def get_entities_with(self, component_type: type) -> List[Entity]:
        """Query entities by component type."""
        return self._component_index.get(component_type, [])
    
    def add_system(self, system: ISystem) -> None:
        """Register a system to be updated."""
        self._systems.append(system)
    
    def update(self, dt: float) -> None:
        """Update all systems."""
        for system in self._systems:
            system.update(dt)
```

#### Task 1.2: Create Entity Factory
```python
# src/world/factories.py

class WorldFactory:
    """Factory for creating world with standard setup."""
    
    @staticmethod
    def create_game_world() -> World:
        world = World()
        
        # Add core systems
        world.add_system(PhysicsSystem())
        world.add_system(PlayerSystem())
        world.add_system(EnemyAISystem())
        world.add_system(CombatSystem())
        world.add_system(RenderSystem())
        
        return world
```

---

### Phase 2: Migrate GameState to World (Week 1-2)

**Goal**: Replace direct dataclass usage with entity-based architecture.

#### Task 2.1: Replace Player Dataclass

**Current**:
```python
@dataclass
class Player:
    x: float = 1.5
    y: float = 1.5
    angle: float = 0.0
    health: int = 100
    # ... 15+ more fields
```

**Target**:
```python
player = PlayerEntity("player")
player.add_component(PositionComponent(1.5, 1.5, 0.0))
player.add_component(HealthComponent(100, 100))
player.add_component(CombatComponent())
player.add_component(PlayerInputComponent())
player.add_component(CollidableComponent(0.3))
world.create_entity(player)
```

#### Task 2.2: Replace Enemy Dataclass

**Current**:
```python
@dataclass
class Enemy:
    x: float
    y: float
    angle: float = 0.0
    health: int = 30
    state: str = "patrol"
    # ... 10+ more fields
```

**Target**:
```python
enemy = EnemyEntity(f"enemy_{i}", enemy_type)
enemy.add_component(PositionComponent(x, y, 0.0))
enemy.add_component(HealthComponent(30, 30))
enemy.add_component(AIComponent(enemy_type))
enemy.add_component(CombatComponent())
enemy.add_component(CollidableComponent(0.4))
world.create_entity(enemy)
```

#### Task 2.3: Update GameEngine

```python
# Before
self.state = GameState()
self.state.player.x = 5.0

# After
self.world = WorldFactory.create_game_world()
player = self.world.get_entities_with(PlayerEntity)[0]
player.get_component(PositionComponent).x = 5.0
```

---

### Phase 3: Component Queries and Filtering (Week 2)

**Goal**: Enable efficient entity queries by component type.

#### Task 3.1: Implement Component Index

```python
def _index_entity(self, entity: Entity) -> None:
    """Index entity by its component types."""
    for comp in entity.components.values():
        comp_type = type(comp)
        if comp_type not in self._component_index:
            self._component_index[comp_type] = []
        if entity not in self._component_index[comp_type]:
            self._component_index[comp_type].append(entity)
```

#### Task 3.2: Create Query Builder

```python
class EntityQuery:
    """Fluent interface for entity queries."""
    
    def __init__(self, world: World):
        self._world = world
        self._required: List[type] = []
        self._excluded: List[type] = []
    
    def with_component(self, component_type: type) -> "EntityQuery":
        self._required.append(component_type)
        return self
    
    def without_component(self, component_type: type) -> "EntityQuery":
        self._excluded.append(component_type)
        return self
    
    def execute(self) -> List[Entity]:
        # Implementation to filter entities
        pass
```

**Usage**:
```python
# Get all living enemies
enemies = (EntityQuery(world)
    .with_component(EnemyEntity)
    .with_component(HealthComponent)
    .without_component_tag("dead")
    .execute())
```

---

### Phase 4: System Refactoring (Week 2-3)

**Goal**: Refactor systems to operate on entities, not dataclasses.

#### Task 4.1: Update PlayerSystem

```python
class PlayerSystem(SystemBase):
    def update(self, dt: float) -> None:
        # Get player from world
        players = self.world.get_entities_with(PlayerInputComponent)
        if not players:
            return
        
        player = players[0]
        position = player.get_component(PositionComponent)
        health = player.get_component(HealthComponent)
        combat = player.get_component(CombatComponent)
        
        # Process input and update components
        # ...
```

#### Task 4.2: Update EnemyAISystem

```python
class EnemyAISystem(SystemBase):
    def update(self, dt: float) -> None:
        # Get all enemies
        enemies = self.world.get_entities_with(AIComponent)
        
        for enemy in enemies:
            ai = enemy.get_component(AIComponent)
            position = enemy.get_component(PositionComponent)
            health = enemy.get_component(HealthComponent)
            
            # Update AI behavior
            # ...
```

#### Task 4.3: Create New Systems

| System | Purpose | Components Used |
|--------|---------|----------------|
| `PhysicsSystem` | Collision detection | Position, Collidable |
| `DamageSystem` | Damage calculation | Health, Combat |
| `InventorySystem` | Item management | Inventory, Collectible |
| `AnimationSystem` | Sprite animations | Animation, Sprite |

---

### Phase 5: Component Lifecycle (Week 3)

**Goal**: Implement proper component/entity lifecycle management.

#### Task 5.1: Component Events

```python
class ComponentLifecycle:
    """Mixin for components that need lifecycle events."""
    
    def on_attach(self) -> None:
        """Called when component is attached to entity."""
        pass
    
    def on_detach(self) -> None:
        """Called when component is removed from entity."""
        pass
    
    def on_destroy(self) -> None:
        """Called when entity is destroyed."""
        pass
```

#### Task 5.2: Entity Events

```python
class EntityEvent:
    """Events emitted by entities."""
    ENTITY_CREATED = "entity_created"
    ENTITY_DESTROYED = "entity_destroyed"
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"
```

---

### Phase 6: Serialization (Week 3-4)

**Goal**: Support saving/loading game state.

#### Task 6.1: Component Serialization

```python
class SerializableComponent(Component):
    """Base for components that can be serialized."""
    
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SerializableComponent":
        raise NotImplementedError
```

#### Task 6.2: World Serialization

```python
def serialize_world(world: World) -> Dict[str, Any]:
    return {
        "entities": [
            {
                "id": e.id,
                "components": {
                    name: comp.to_dict()
                    for name, comp in e.components.items()
                }
            }
            for e in world._entities.values()
        ]
    }
```

---

## Implementation Tasks Summary

### Phase 1: Foundation
| Task | Description | Files to Create/Modify |
|------|-------------|------------------------|
| T1.1 | Create World class | `src/world/__init__.py`, `src/world/world.py` |
| T1.2 | Create WorldFactory | `src/world/factories.py` |
| T1.3 | Create EntityQuery | `src/world/query.py` |

### Phase 2: Migration
| Task | Description | Files to Modify |
|------|-------------|-----------------|
| T2.1 | Update GameEngine to use World | `src/engine/game_engine.py` |
| T2.2 | Remove Player dataclass usage | `src/engine/game_state.py` |
| T2.3 | Remove Enemy dataclass usage | `src/engine/game_state.py` |

### Phase 3: Systems
| Task | Description | Files to Modify |
|------|-------------|-----------------|
| T3.1 | Refactor PlayerSystem | `src/systems/player_system.py` |
| T3.2 | Refactor EnemyAISystem | `src/systems/enemy_ai_system.py` |
| T3.3 | Refactor CombatSystem | `src/systems/combat_system.py` |
| T3.4 | Create PhysicsSystem | `src/systems/physics_system.py` |

### Phase 4: Components
| Task | Description | Files to Create |
|------|-------------|----------------|
| T4.1 | Add InventoryComponent | `src/entities/components.py` |
| T4.2 | Add AnimationComponent | `src/entities/components.py` |
| T4.3 | Add VelocityComponent | `src/entities/components.py` |
| T4.4 | Add WeaponComponent | `src/entities/components.py` |

### Phase 5: Lifecycle
| Task | Description | Files to Modify |
|------|-------------|-----------------|
| T5.1 | Add lifecycle methods | `src/entities/base.py` |
| T5.2 | Add entity events | `src/engine/event_system.py` |

---

## Migration Strategy

### Backward Compatibility

1. **Parallel Operation**: Keep both old and new systems running during transition
2. **Gradual Migration**: Move one entity type at a time (Player → Enemies → Items)
3. **Feature Flags**: Use config to switch between architectures

### Testing Strategy

1. **Unit Tests**: Test components in isolation
2. **Integration Tests**: Test entity interactions
3. **System Tests**: Test complete game loops

### Performance Considerations

1. **Lazy Indexing**: Only index components when queried
2. **Object Pooling**: Reuse entities to avoid GC pressure
3. **Cache-Friendly Layout**: Group component data for CPU cache

---

## Code Examples

### Creating a Complete Entity

```python
from world import World
from entities import (
    Entity, PositionComponent, HealthComponent,
    CombatComponent, CollidableComponent, AIComponent
)

world = World()

# Create a demon enemy
demon = Entity("demon_1")
demon.add_component(PositionComponent(5.0, 3.0, 0.0))
demon.add_component(HealthComponent(60, 60))
demon.add_component(AIComponent(enemy_type="demon"))
demon.add_component(CombatComponent(
    attack_range=1.0,
    attack_damage=15,
    attack_cooldown=1.0
))
demon.add_component(CollidableComponent(0.4))

world.create_entity(demon)
```

### Querying Entities

```python
# Get all enemies within range of player
player_pos = world.get_entities_with(PositionComponent)[0].get_component(PositionComponent)

enemies = (EntityQuery(world)
    .with_component(AIComponent)
    .execute())

for enemy in enemies:
    pos = enemy.get_component(PositionComponent)
    dist = pos.distance_to(player_pos.x, player_pos.y)
    if dist < 10.0:
        # Attack!
        pass
```

### Creating a Custom Component

```python
class InventoryComponent(Component):
    def __init__(self, capacity: int = 10):
        super().__init__()
        self.capacity = capacity
        self._items: List[Item] = []
    
    def add_item(self, item: Item) -> bool:
        if len(self._items) >= self.capacity:
            return False
        self._items.append(item)
        return True
    
    def remove_item(self, item_id: str) -> Optional[Item]:
        for item in self._items:
            if item.id == item_id:
                self._items.remove(item)
                return item
        return None
    
    def get_items(self) -> List[Item]:
        return self._items.copy()
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|--------------|
| Entity Usage | 100% of game objects use Entity | Code review |
| Component Queries | < 1ms for 1000 entities | Benchmark |
| Test Coverage | > 80% | pytest --cov |
| System Coupling | < 5 imports per system | Code analysis |
| Migration Complete | All dataclasses removed | Code review |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance regression | High | Benchmark before/after each phase |
| Breaking existing functionality | High | Keep both systems during transition |
| Over-engineering | Medium | Keep components simple, avoid deep hierarchies |
| Learning curve | Medium | Documentation and examples |

---

## Appendix: File Structure After Transformation

```
src/
├── main.py
├── config.py
├── game.py
├── renderer.py
│
├── world/                     # NEW - Central entity management
│   ├── __init__.py
│   ├── world.py              # World class
│   ├── factories.py          # WorldFactory
│   ├── query.py             # EntityQuery builder
│   └── events.py            # Entity events
│
├── entities/                  # Entity-Component system
│   ├── base.py              # Entity, Component bases
│   ├── components.py         # All component classes
│   ├── player.py            # PlayerEntity
│   ├── enemy.py             # EnemyEntity
│   ├── item.py              # ItemEntity (NEW)
│   └── factory.py           # EntityFactory
│
├── systems/                   # Game systems
│   ├── base.py              # SystemBase, ISystem
│   ├── player_system.py     # PlayerSystem (refactored)
│   ├── enemy_ai_system.py   # EnemyAISystem (refactored)
│   ├── combat_system.py    # CombatSystem (refactored)
│   ├── physics_system.py   # NEW - PhysicsSystem
│   ├── damage_system.py   # NEW - DamageSystem
│   └── inventory_system.py # NEW - InventorySystem
│
├── engine/
│   ├── game_engine.py       # Uses World
│   ├── game_state.py       # Will be simplified/removed
│   ├── event_system.py
│   └── system_registry.py  # Can be replaced by World
│
├── physics/
│   ├── interfaces.py
│   └── physics.py
│
├── input/
│   ├── actions.py
│   ├── bindings.py
│   └── manager.py
│
└── ui/
    ├── interfaces.py
    ├── manager.py
    ├── menu.py
    ├── hud.py
    └── console.py
```

---

## Questions and Proposals for Review

### Q1: Backward Compatibility Duration

**Question**: How long should we maintain backward compatibility with the old dataclass-based system?

**Answer**: **Option B (Aggressive)** - Remove old code immediately after migration (1 sprint)

**Updated Plan**: 
- No parallel operation phase
- Immediate switch after migration testing
- Single sprint for complete migration
- Risk: Higher, but faster delivery

---

### Q2: Component Data Layout (SoA vs AoS)

**Question**: Should we use Structure of Arrays (SoA) for better cache performance or Array of Structures (AoS) for simplicity?

**Answer**: Keep AoS for Phase 1-2, consider SoA later if performance testing shows it necessary

**Updated Plan**: 
- Phase 1-2: AoS (current approach)
- Phase 3+: Profile first, then decide
- WebDoom scale (<100 entities) makes this premature optimization

---

### Q3: Entity ID Generation

**Question**: How should we generate unique entity IDs?

**Answer**: Simple strings - `"player"`, `"enemy_1"`, `"enemy_2"`

**Updated Plan**: 
- Keep current string-based approach
- Add helper method for auto-numbered IDs: `world.create_entity_id("enemy")` → `"enemy_0"`, `"enemy_1"`

---

### Q4: System Update Order

**Question**: Should we hardcode system update order or use a priority system?

**Answer**: **Option C (Event-driven)** - systems subscribe to specific events

**Updated Plan**:
- Systems don't iterate automatically
- Instead, subscribe to events like:
  - `EntityEvent.COMPONENT_ADDED`
  - `EntityEvent.ENTITY_CREATED`
  - Custom game events (attack, damage, death)
- Allows more decoupled architecture
- World maintains event bus

---

### Q5: Should We Keep SystemRegistry or Replace It?

**Question**: The codebase currently has SystemRegistry. Should we keep it or replace with World?

**Answer**: Replace SystemRegistry with World

**Updated Plan**:
- World becomes single coordinator
- Remove SystemRegistry entirely
- Migration: `system_registry.update_all(dt)` → `world.update(dt)`

---

### Q6: Item/Inventory System Priority

**Question**: Should we implement the inventory system as part of this transformation or as a separate feature?

**Answer**: **Defer** to separate feature/epic

**Updated Plan**:
- Remove InventorySystem from Phase 4
- Add placeholder `InventoryComponent` to components.py
- Document inventory as future enhancement

---

### Q7: Testing Strategy

**Question**: How should we test the new architecture?

**Answer**: 
- Unit Tests ✓
- Integration Tests ✓
- System Tests ✓
- E2E Tests - Note: It's pygame game, not browser - need alternative for X window
- Add benchmark tests ✓

**Updated Plan for E2E**:
- Use `pygame.HEADLESS` or `SDL_VIDEODRIVER=dummy` for CI testing
- Consider `pytest pygame` plugin for unit-style E2E tests
- Add performance benchmarks in `tests/benchmarks/`

---

### Q8: Renderer Integration

**Question**: How should the Renderer interact with the new entity system?

**Answer**: **Option A** - Query World directly

**Updated Plan**:
- Renderer calls `world.get_entities_with(PositionComponent)`
- No intermediate dataclasses
- Keep Renderer decoupled from entity system

---

### Q9: Serialization Scope

**Question**: Should serialization include complete game state (maps, entities, systems)?

**Answer**: Yes, implement serialization (MVP: entities only, skip maps/systems)

**Updated Plan**:
- Phase 6: Full entity/component serialization
- Skip: Systems (stateless), Maps (handled by MapManager)
- Include: Entities, Components, World state

---

### Q10: Performance Budget

**Question**: What are acceptable performance targets for entity queries?

**Answer**: As recommended (keep targets)

**Updated Targets**:
| Operation | Target | Maximum |
|-----------|--------|---------|
| Entity creation | < 1ms | 5ms |
| Component query (100 entities) | < 0.1ms | 1ms |
| Full world update | < 16ms | 33ms (30 FPS) |

---

### Additional Proposals

**P1: Add "Tags" to Entities** → Approved

**P2: Component Validation** → Approved

**P3: Prototype Pattern** → Approved

---

*Last updated: 2026*
*Review Status: APPROVED - Ready for implementation*

---

## New Questions from Second Revision

### Q11: Event-Driven System Implementation

**Question**: For event-driven systems (Q4), how should we integrate with the existing EventSystem?

**Answer**: **Option A** - Extend existing `EventSystem` with entity events

**Updated Plan**:
- Add entity events to existing EventSystem
- New events: `ENTITY_CREATED`, `ENTITY_DESTROYED`, `COMPONENT_ADDED`, `COMPONENT_REMOVED`
- Systems subscribe to relevant events
- World emits events on entity lifecycle

---

### Q12: E2E Testing Tools for Pygame

**Question**: What tools should we use for E2E testing given it's a pygame game?

**Answer**: **All three options** - pytest-pygame + custom headless + screenshot comparison

**Updated Plan**:
- Option A: `pytest-pygame` for unit-style game logic tests
- Option B: Custom headless runner with `SDL_VIDEODRIVER=dummy`
- Option C: Screenshot comparison for renderer verification
- Add `tests/benchmarks/` for performance testing

---

### Q13: Phase Task Updates

**Question**: Based on approved answers, should we update the task list in the document?

**Answer**: **Yes** - Update all tasks and phases

---

## Implementation Tasks Summary (UPDATED)

### Phase 1: Foundation (Week 1)
| Task | Description | Files to Create/Modify |
|------|-------------|------------------------|
| T1.1 | Create World class with event integration | `src/world/__init__.py`, `src/world/world.py` |
| T1.2 | Create WorldFactory | `src/world/factories.py` |
| T1.3 | Create EntityQuery with tags | `src/world/query.py` |
| T1.4 | Add tags system to Entity base | `src/entities/base.py` |
| T1.5 | Add prototype pattern to World | `src/world/world.py` |
| T1.6 | Extend EventSystem with entity events | `src/engine/event_system.py` |

### Phase 2: Migration (Week 1-2)
| Task | Description | Files to Modify |
|------|-------------|-----------------|
| T2.1 | Create World in GameEngine (replace SystemRegistry) | `src/engine/game_engine.py` |
| T2.2 | Remove Player dataclass usage | `src/engine/game_state.py` |
| T2.3 | Remove Enemy dataclass usage | `src/engine/game_state.py` |
| T2.4 | Migrate to event-driven system updates | `src/systems/*.py` |

### Phase 3: Systems (Week 2)
| Task | Description | Files to Modify |
|------|-------------|-----------------|
| T3.1 | Refactor PlayerSystem with event subscription | `src/systems/player_system.py` |
| T3.2 | Refactor EnemyAISystem with event subscription | `src/systems/enemy_ai_system.py` |
| T3.3 | Refactor CombatSystem with event subscription | `src/systems/combat_system.py` |
| T3.4 | Create PhysicsSystem | `src/systems/physics_system.py` |

### Phase 4: Components (Week 2-3)
| Task | Description | Files to Create/Modify |
|------|-------------|------------------------|
| T4.1 | Add placeholder InventoryComponent | `src/entities/components.py` |
| T4.2 | Add TagComponent | `src/entities/components.py` |
| T4.3 | Add PrototypeComponent | `src/entities/components.py` |
| T4.4 | Add AnimationComponent (placeholder) | `src/entities/components.py` |

### Phase 5: Lifecycle & Testing (Week 3)
| Task | Description | Files to Modify |
|------|-------------|-----------------|
| T5.1 | Add lifecycle methods to Entity/Component | `src/entities/base.py` |
| T5.2 | Add entity event emission in World | `src/world/world.py` |
| T5.3 | Setup E2E testing (pytest-pygame + headless) | `tests/` |
| T5.4 | Add performance benchmarks | `tests/benchmarks/` |

### Phase 6: Serialization (Week 3-4)
| Task | Description | Files to Create/Modify |
|------|-------------|------------------------|
| T6.1 | Add SerializableComponent base | `src/entities/base.py` |
| T6.2 | Implement component serialization | `src/entities/components.py` |
| T6.3 | Implement World serialization | `src/world/world.py` |
| T6.4 | Add save/load functions | `src/world/serialization.py` |

---

*Last updated: 2026*
*Review Status: FINAL - Implementation Ready*

---

## Final Review Checklist

Before starting implementation, verify:

- [x] All questions answered
- [x] Task list updated with new phases
- [x] Phase 1: World, Tags, Prototype, Event integration
- [x] Phase 2: Replace SystemRegistry, remove dataclasses
- [x] Phase 3: Event-driven systems
- [x] Phase 4: Placeholder components (no inventory)
- [x] Phase 5: E2E testing setup
- [x] Phase 6: Serialization

**Ready to Start**: Phase 1 implementation