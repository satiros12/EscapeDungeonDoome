"""
Performance benchmarks for entity creation

Benchmarks various entity creation scenarios:
- Single entity creation
- Bulk enemy creation
- Entity cloning
- Component queries
"""

import os
import sys
import pytest
import time

# Set headless mode before importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Ensure src directory is at the front of the path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
src_path = os.path.join(project_root, "src")

# Remove any existing config/module conflicts
for mod in list(sys.modules.keys()):
    if mod == "config" or mod.startswith("config.") or mod.startswith("src."):
        if "site-packages" not in str(getattr(sys.modules.get(mod), "__file__", "")):
            del sys.modules[mod]

# Insert src at the front
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture(scope="module")
def world():
    """Create a World instance for benchmarking."""
    from world.world import World
    from engine.event_system import EventSystem

    event_system = EventSystem()
    return World(event_system)


@pytest.fixture(scope="module")
def entity_factory():
    """Create an EntityFactory for benchmarking."""
    from entities.factory import EntityFactory

    return EntityFactory()


def test_single_entity_creation(world, benchmark):
    """Benchmark single entity creation."""
    from entities.player import PlayerEntity

    def create_entity():
        entity = PlayerEntity(f"bench_entity_{time.time()}")
        world.create_entity(entity)
        world.destroy_entity(entity)

    # Run benchmark
    benchmark.pedantic(create_entity, rounds=100)


def test_player_entity_creation(world, entity_factory, benchmark):
    """Benchmark player entity creation."""

    def create_player():
        player = entity_factory.create_player("bench_player")
        world.create_entity(player)
        # Clean up for next iteration
        world.destroy_entity(player)

    # Run benchmark
    benchmark.pedantic(create_player, rounds=100)


def test_enemy_entity_creation(world, entity_factory, benchmark):
    """Benchmark enemy entity creation."""

    def create_enemy():
        enemy = entity_factory.create_enemy("imp", 5.0, 5.0)
        world.create_entity(enemy)
        # Clean up for next iteration
        world.destroy_entity(enemy)

    # Run benchmark
    benchmark.pedantic(create_enemy, rounds=100)


def test_bulk_enemy_creation(world, entity_factory, benchmark):
    """Benchmark bulk enemy creation (100 enemies)."""

    def create_bulk_enemies():
        enemies = []
        for i in range(100):
            enemy = entity_factory.create_enemy("imp", float(i), float(i))
            world.create_entity(enemy)
            enemies.append(enemy)

        # Clean up
        for enemy in enemies:
            world.destroy_entity(enemy)

    # Run benchmark
    benchmark.pedantic(create_bulk_enemies, rounds=10)


def test_query_by_single_component(world, entity_factory, benchmark):
    """Benchmark querying entities by single component."""
    # Create 50 entities with various components
    for i in range(50):
        entity = entity_factory.create_enemy("imp", float(i), float(i))
        world.create_entity(entity)

    from entities.components import PositionComponent

    def run_query():
        return world.get_entities_with(PositionComponent)

    # Run benchmark
    benchmark.pedantic(run_query, rounds=100)

    # Cleanup
    world.clear()


def test_query_by_multiple_components(world, entity_factory, benchmark):
    """Benchmark querying entities by multiple components."""
    # Create 50 entities with various components
    for i in range(50):
        entity = entity_factory.create_enemy("imp", float(i), float(i))
        world.create_entity(entity)

    from entities.components import PositionComponent, HealthComponent

    def run_query():
        return world.get_entities_with(PositionComponent, HealthComponent)

    # Run benchmark
    benchmark.pedantic(run_query, rounds=100)

    # Cleanup
    world.clear()


def test_entity_cloning(world, entity_factory, benchmark):
    """Benchmark entity cloning."""
    # Create source entity
    source_entity = entity_factory.create_enemy("imp", 5.0, 5.0)
    world.create_entity(source_entity)

    def clone_entity():
        return world.clone_entity(source_entity, f"clone_{time.time()}")

    # Run benchmark
    benchmark.pedantic(clone_entity, rounds=50)

    # Cleanup
    world.clear()


def test_world_update_empty(benchmark):
    """Benchmark world update with no entities."""
    from world.world import World
    from engine.event_system import EventSystem
    from systems.player_system import PlayerSystem
    from systems.enemy_ai_system import EnemyAISystem
    from systems.combat_system import CombatSystem
    from engine.game_state import GameState

    event_system = EventSystem()
    world = World(event_system)
    # Add game_state attribute that systems expect
    world.game_state = GameState()
    world.game_state.game_state = "playing"

    world.add_system(PlayerSystem(world, event_system))
    world.add_system(EnemyAISystem(world, event_system))
    world.add_system(CombatSystem(world, event_system))

    def update_world():
        world.update(0.016)

    # Run benchmark
    benchmark.pedantic(update_world, rounds=100)


def test_world_update_with_entities(benchmark):
    """Benchmark world update with entities."""
    from world.world import World
    from engine.event_system import EventSystem
    from systems.player_system import PlayerSystem
    from systems.enemy_ai_system import EnemyAISystem
    from systems.combat_system import CombatSystem
    from entities.factory import EntityFactory
    from engine.game_state import GameState

    event_system = EventSystem()
    world = World(event_system)
    # Add game_state attribute that systems expect
    world.game_state = GameState()
    world.game_state.game_state = "playing"

    world.add_system(PlayerSystem(world, event_system))
    world.add_system(EnemyAISystem(world, event_system))
    world.add_system(CombatSystem(world, event_system))

    # Add entities
    factory = EntityFactory()
    for i in range(10):
        enemy = factory.create_enemy("imp", float(i), float(i))
        world.create_entity(enemy)

    def update_world():
        world.update(0.016)

    # Run benchmark
    benchmark.pedantic(update_world, rounds=100)


def test_collision_check(benchmark):
    """Benchmark collision checking."""
    from physics import Physics

    physics = Physics()
    # Simple test map
    grid = [
        "##########",
        "#........#",
        "#........#",
        "#........#",
        "##########",
    ]
    physics.set_map(grid)

    def check_collision():
        return physics.check_collision(2.5, 2.5)

    # Run benchmark
    benchmark.pedantic(check_collision, rounds=1000)


def test_raycast(benchmark):
    """Benchmark raycasting."""
    from physics import Physics

    physics = Physics()
    # Simple test map
    grid = [
        "##########",
        "#........#",
        "#........#",
        "#........#",
        "##########",
    ]
    physics.set_map(grid)

    def cast_ray():
        return physics.cast_ray(0.0, 1.5, 1.5)

    # Run benchmark
    benchmark.pedantic(cast_ray, rounds=1000)


# Pytest-benchmark configuration
def pytest_configure(config):
    """Configure pytest-benchmark."""
    config.addinivalue_line(
        "markers", "slow: marks benchmarks as slow (deselect with '-m \"not slow\"')"
    )
