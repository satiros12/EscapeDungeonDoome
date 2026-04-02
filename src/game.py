"""
Game facade - coordinates all game components
"""

import pygame
import math
from typing import Dict, Optional

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, MAX_DEPTH
from input_handler import InputHandler
from renderer import Renderer
from engine.game_engine import GameEngine
from ui.menu import Menu, MenuItem, create_main_menu
from ui.hud import HUD
from ui.console import Console


class Game:
    """Main game class that coordinates all systems."""

    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("WebDoom - Pygame Edition")

        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Create components
        self.input_handler = InputHandler()
        self.renderer = Renderer(self.screen)
        self.game_engine = GameEngine(self.screen)
        self.hud = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.console = Console(self.screen)

        # Game state
        self.running = True
        self.current_menu = None
        self._create_menus()

    def _create_menus(self) -> None:
        """Create menu system with callbacks."""
        self.main_menu = create_main_menu()

        # Wire up menu callbacks
        self.main_menu.items[0].callback = self._on_start_game  # Start Game
        self.main_menu.items[1].callback = self._on_options  # Options (placeholder)
        self.main_menu.items[2].callback = self._on_quit  # Quit

    def _on_start_game(self) -> None:
        """Callback for start game menu item."""
        self.game_engine.start_game()
        self.current_menu = None

    def _on_options(self) -> None:
        """Callback for options menu item."""
        # Placeholder - could open options menu
        pass

    def _on_quit(self) -> None:
        """Callback for quit menu item."""
        self.running = False

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0

            # Handle events
            self._handle_events()

            # Update game state
            self._update(dt)

            # Render
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Pass events to appropriate handler
            if self.game_engine.state.game_state == "menu":
                self._handle_menu_events(event)
            elif self.game_engine.state.game_state == "pause":
                self._handle_pause_events(event)
            elif self.game_engine.state.game_state == "playing":
                self._handle_playing_events(event)

    def _handle_menu_events(self, event: pygame.event.Event) -> None:
        """Handle events while in menu state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key in (
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_RETURN,
                pygame.K_w,
                pygame.K_s,
            ):
                # Pass all navigation keys to menu handler
                self.main_menu.handle_input(event)
        elif event.type == pygame.KEYUP:
            pass  # Menu doesn't need key up events

    def _handle_pause_events(self, event: pygame.event.Event) -> None:
        """Handle events while paused."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.resume_game()
            elif event.key == pygame.K_p:
                self.console.toggle()

    def _handle_playing_events(self, event: pygame.event.Event) -> None:
        """Handle events while playing."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.pause_game()
            elif event.key == pygame.K_p:
                self.console.toggle()
            elif event.key == pygame.K_SPACE:
                self.game_engine.state.pending_input["Space"] = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.game_engine.state.pending_input["Space"] = False

    def _update(self, dt: float) -> None:
        """Update game state."""
        # Always update input handler
        self.input_handler.update()

        # Get input state
        input_state = self.input_handler.get_keys()

        # Update game engine based on state
        state = self.game_engine.state.game_state

        if state == "menu":
            # Update menu animations
            self.main_menu.update(dt)

        elif state == "playing":
            # Pass input to game engine
            self.game_engine.state.pending_input = input_state.copy()
            self.game_engine.update(dt)

            # Check for game over conditions
            if self.game_engine.state.player.health <= 0:
                self.game_engine.state.game_state = "defeat"

            # Check for victory
            alive_enemies = [
                e
                for e in self.game_engine.state.enemies
                if e.state not in ("dead", "dying")
            ]
            if len(alive_enemies) == 0:
                self.game_engine.state.game_state = "victory"

        elif state == "pause":
            # Game is paused, don't update
            pass

        # Update console if active
        if self.console.active:
            self.console.update(input_state)

    def _render(self) -> None:
        """Render the game."""
        state = self.game_engine.state.game_state

        if state == "menu":
            self._render_menu()
        elif state == "playing":
            self._render_playing()
        elif state == "pause":
            self._render_pause()
        elif state == "victory":
            self._render_victory()
        elif state == "defeat":
            self._render_defeat()

        # Render console on top if active
        if self.console.active:
            self.console.render()

        # Flip display
        self.renderer.present()

    def _render_menu(self) -> None:
        """Render main menu."""
        self.renderer.clear((0, 0, 0))
        self.main_menu.render(self.screen)

    def _render_playing(self) -> None:
        """Render the game while playing."""
        # Clear screen
        self.renderer.clear((0, 0, 0))

        # Get raycasting data from engine
        wall_distances = self.game_engine.get_ray_data()
        player = self.game_engine.state.player

        # Render floor and ceiling
        self.renderer.render_floor_ceiling()

        # Render walls using raycasting
        self.renderer.render_walls_raycasted(
            player, wall_distances, self.game_engine.state.map_manager.get_current_map()
        )

        # Render enemies as sprites
        self.renderer.render_enemies(
            player,
            self.game_engine.state.enemies,
            self.game_engine.state.map_manager.get_current_map(),
        )

        # Render crosshair
        self.renderer.render_crosshair()

        # Render HUD
        self.hud.render(
            self.screen,
            player.health,
            self.game_engine.state.kills,
            "fists",  # Could be extended to weapon system
        )

    def _render_pause(self) -> None:
        """Render pause screen."""
        # First render the game state behind
        self._render_playing()

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Pause text
        self.renderer.render_text(
            "PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, (255, 255, 255), 48
        )
        self.renderer.render_text(
            "Press ESC to resume",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            (200, 200, 200),
            24,
        )

    def _render_victory(self) -> None:
        """Render victory screen."""
        self.renderer.clear((0, 50, 0))

        self.renderer.render_text(
            "VICTORY!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, (255, 255, 0), 64
        )
        self.renderer.render_text(
            f"You killed {self.game_engine.state.kills} enemies!",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 20,
            (255, 255, 255),
            32,
        )
        self.renderer.render_text(
            "Press ESC to quit",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            (200, 200, 200),
            24,
        )

    def _render_defeat(self) -> None:
        """Render defeat screen."""
        self.renderer.clear((50, 0, 0))

        self.renderer.render_text(
            "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, (255, 0, 0), 64
        )
        self.renderer.render_text(
            f"You killed {self.game_engine.state.kills} enemies",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 20,
            (255, 255, 255),
            32,
        )
        self.renderer.render_text(
            "Press ESC to quit",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            (200, 200, 200),
            24,
        )


if __name__ == "__main__":
    game = Game()
    game.run()
