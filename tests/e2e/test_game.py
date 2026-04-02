"""
E2E tests for game initialization and basic functionality

Tests the full game initialization flow including:
- GameEngine creation
- Map loading
- Player and enemy spawning
- Game state transitions
"""

import pytest


class TestGameInitialization:
    """Test game initialization and startup."""

    def test_game_engine_creation(self, game_engine):
        """Test that GameEngine can be created successfully."""
        assert game_engine is not None
        assert game_engine.state is not None
        assert game_engine.world is not None

    def test_game_starts_in_menu_state(self, game_engine):
        """Test that game starts in menu state."""
        assert game_engine.state.game_state == "menu"

    def test_game_can_transition_to_playing(self, game_engine):
        """Test that game can transition from menu to playing."""
        game_engine.start_game()
        assert game_engine.state.game_state == "playing"

    def test_map_loads_on_start(self, game_engine):
        """Test that map is loaded when game starts."""
        game_engine.start_game()

        # Map should be loaded
        assert game_engine.state.map_manager is not None
        grid = game_engine.state.map_manager.get_current_map().get("grid")
        assert grid is not None
        assert len(grid) > 0

    def test_player_spawns_on_start(self, game_engine):
        """Test that player entity is created when game starts."""
        game_engine.start_game()

        # Player should exist and have valid position
        assert game_engine.state.player is not None
        assert game_engine.state.player.x > 0
        assert game_engine.state.player.y > 0

    def test_enemies_spawn_on_start(self, game_engine):
        """Test that enemies are spawned when game starts."""
        game_engine.start_game()

        # Should have enemies in default map (actual count may vary)
        assert len(game_engine.state.enemies) > 0

    def test_physics_map_set_on_start(self, game_engine):
        """Test that physics system receives map grid on start."""
        game_engine.start_game()

        # Physics should have map grid set
        grid = game_engine.state.map_manager.get_current_map().get("grid")
        assert game_engine.physics._grid is not None
        assert game_engine.physics._grid == grid


class TestGameStateTransitions:
    """Test game state transitions."""

    def test_game_can_be_paused(self, game_engine_with_loaded_map):
        """Test that game can be paused."""
        engine = game_engine_with_loaded_map

        engine.pause_game()
        assert engine.state.game_state == "pause"
        assert engine.paused is True

    def test_game_can_be_resumed(self, game_engine_with_loaded_map):
        """Test that game can be resumed from pause."""
        engine = game_engine_with_loaded_map

        engine.pause_game()
        engine.resume_game()

        assert engine.state.game_state == "playing"
        assert engine.paused is False

    def test_cannot_pause_from_menu(self, game_engine):
        """Test that game cannot be paused from menu state."""
        # Game starts in menu
        engine = game_engine
        engine.pause_game()

        # Should remain in menu state
        assert engine.state.game_state == "menu"


class TestGameUpdate:
    """Test game update loop."""

    def test_game_update_runs_without_error(self, game_engine_with_loaded_map):
        """Test that game update runs without errors."""
        engine = game_engine_with_loaded_map

        # Run a few updates
        for _ in range(10):
            engine.update(0.016)  # ~60 FPS

        # Should still be in playing state
        assert engine.state.game_state == "playing"

    def test_raycasting_data_generated(self, game_engine_with_loaded_map):
        """Test that raycasting data is generated during update."""
        engine = game_engine_with_loaded_map

        engine.update(0.016)

        # Should have ray distances
        assert len(engine.wall_distances) > 0
        assert all(d >= 0 for d in engine.wall_distances)


class TestPlayerActions:
    """Test player actions."""

    def test_player_can_attack(self, game_engine_with_loaded_map):
        """Test that player can perform attack action."""
        engine = game_engine_with_loaded_map

        # Player should be able to attack without error
        engine.attack()

    def test_player_has_health(self, game_engine_with_loaded_map):
        """Test that player has health after initialization."""
        engine = game_engine_with_loaded_map

        assert engine.state.player.health > 0


class TestWorldEntityManagement:
    """Test world entity management."""

    def test_world_creation(self, world):
        """Test that world can be created."""
        assert world is not None
        assert len(world.entities) == 0

    def test_world_can_create_entity(self, world):
        """Test that world can create entities."""
        from entities.player import PlayerEntity

        entity = PlayerEntity("test_entity")
        world.create_entity(entity)

        assert "test_entity" in world.entities
        # Clean up
        world.destroy_entity(entity)

    def test_world_can_query_entities(self, world):
        """Test that world can query entities by component."""
        from entities.player import PlayerEntity
        from entities.components import PositionComponent, HealthComponent

        entity = PlayerEntity("test_entity")
        entity.add_component(PositionComponent(1.0, 2.0), "position")
        entity.add_component(HealthComponent(100, 100), "health")
        world.create_entity(entity)

        # Query by PositionComponent
        entities_with_position = world.get_entities_with(PositionComponent)
        assert len(entities_with_position) == 1

        # Query by multiple components
        entities_with_both = world.get_entities_with(PositionComponent, HealthComponent)
        assert len(entities_with_both) == 1

        # Clean up
        world.destroy_entity(entity)

    def test_world_can_destroy_entity(self, world):
        """Test that world can destroy entities."""
        from entities.player import PlayerEntity

        entity = PlayerEntity("test_entity")
        world.create_entity(entity)
        assert "test_entity" in world.entities

        world.destroy_entity(entity)
        assert "test_entity" not in world.entities
