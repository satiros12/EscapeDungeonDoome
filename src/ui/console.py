"""
Console - debug console for console commands
"""

import pygame
from typing import List, Callable, Dict


class Console:
    """Debug console for entering console commands."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.active = False
        self.input_text = ""
        self.output_lines: List[str] = []
        self.max_output_lines = 10

        # Commands registry
        self.commands: Dict[str, Callable] = {}

        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.text_color = (0, 255, 0)
        self.input_color = (255, 255, 255)

    def register_command(self, name: str, callback: Callable) -> None:
        """Register a console command."""
        self.commands[name.lower()] = callback

    def toggle(self) -> None:
        """Toggle console visibility."""
        self.active = not self.active
        if self.active:
            self.input_text = ""

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle console input. Returns True if handled."""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return True
            elif event.key == pygame.K_RETURN:
                self._execute_command()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.unicode.isprintable():
                self.input_text += event.unicode
                return True

        return False

    def _execute_command(self) -> None:
        """Execute the current command."""
        if not self.input_text.strip():
            return

        parts = self.input_text.split()
        cmd = parts[0].lower()
        args = parts[1:]

        self.output_lines.append(f"> {self.input_text}")

        if cmd in self.commands:
            try:
                result = self.commands[cmd](*args)
                if result is not None:
                    self.output_lines.append(str(result))
            except Exception as e:
                self.output_lines.append(f"Error: {e}")
        else:
            self.output_lines.append(f"Unknown command: {cmd}")

        # Keep only last max_output_lines
        if len(self.output_lines) > self.max_output_lines:
            self.output_lines = self.output_lines[-self.max_output_lines :]

        self.input_text = ""

    def render(self) -> None:
        """Render the console."""
        if not self.active:
            return

        # Create semi-transparent background
        overlay = pygame.Surface((self.screen_width, 200))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, self.screen_height - 200))

        # Render output lines
        font = pygame.font.Font(None, 20)
        for i, line in enumerate(self.output_lines):
            text_surface = font.render(line, True, self.text_color)
            self.screen.blit(text_surface, (10, self.screen_height - 200 + 10 + i * 20))

        # Render input
        input_surface = font.render(f"> {self.input_text}", True, self.input_color)
        self.screen.blit(input_surface, (10, self.screen_height - 30))

    def add_output(self, text: str) -> None:
        """Add a line to console output."""
        self.output_lines.append(text)
        if len(self.output_lines) > self.max_output_lines:
            self.output_lines = self.output_lines[-self.max_output_lines :]


def create_debug_console(screen: pygame.Surface) -> Console:
    """Create a console with debug commands."""
    console = Console(screen)

    # Register default debug commands
    console.register_command(
        "help", lambda: "Available commands: god, noclip, health, killall"
    )
    console.register_command("god", lambda: "God mode toggled")
    console.register_command(
        "health",
        lambda args: f"Health: 100" if not args else f"Set health to {args[0]}",
    )

    return console
