"""
Pytest configuration and fixtures for E2E tests

Provides fixtures for:
- Headless pygame initialization (SDL_VIDEODRIVER=dummy)
- GameEngine fixture
- World fixture
"""

import os
import sys
import pytest

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


@pytest.fixture(scope="session")
def pygame_initialized():
    """Initialize pygame in headless mode for the test session."""
    import pygame

    # Initialize pygame with dummy video driver
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal window for headless

    yield pygame

    # Cleanup
    pygame.quit()


@pytest.fixture
def mock_screen(pygame_initialized):
    """Create a mock pygame screen for testing."""
    import pygame

    # Create a small test screen
    screen = pygame.Surface((800, 600))
    return screen


@pytest.fixture
def game_engine(mock_screen):
    """Create a GameEngine instance for testing."""
    from engine.game_engine import GameEngine

    engine = GameEngine(mock_screen)
    return engine


@pytest.fixture
def world():
    """Create a World instance for testing."""
    from world.world import World
    from engine.event_system import EventSystem

    event_system = EventSystem()
    world = World(event_system)
    return world


@pytest.fixture
def game_engine_with_loaded_map(mock_screen):
    """Create a GameEngine with map already loaded."""
    from engine.game_engine import GameEngine

    engine = GameEngine(mock_screen)
    engine.start_game()
    return engine


@pytest.fixture
def game_state():
    """Create a GameState instance for testing."""
    from engine.game_state import GameState

    state = GameState()
    return state


@pytest.fixture
def game_state_with_map():
    """Create a GameState with map already loaded."""
    from engine.game_state import GameState

    state = GameState()
    state.parse_map()
    return state
