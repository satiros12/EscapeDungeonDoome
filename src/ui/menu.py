"""
Menu system for game menus
"""

import pygame
from typing import List, Callable


class MenuItem:
    """Represents a single menu item."""

    def __init__(self, text: str, callback: Callable = None):
        self.text = text
        self.callback = callback


class Menu:
    """Simple menu system."""

    def __init__(self, title: str, items: List[MenuItem]):
        self.title = title
        self.items = items
        self.selected_index = 0
        self.font_size = 36
        self.item_spacing = 50

    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                item = self.items[self.selected_index]
                if item.callback:
                    item.callback()

    def render(self, screen: pygame.Surface) -> None:
        """Render the menu."""
        font = pygame.font.Font(None, self.font_size)
        title_font = pygame.font.Font(None, self.font_size + 20)

        # Render title
        title_surface = title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_surface, title_rect)

        # Render menu items
        start_y = 200
        for i, item in enumerate(self.items):
            color = (255, 255, 255) if i == self.selected_index else (128, 128, 128)
            text_surface = font.render(item.text, True, color)
            text_rect = text_surface.get_rect(
                center=(screen.get_width() // 2, start_y + i * self.item_spacing)
            )
            screen.blit(text_surface, text_rect)

    def get_selected_item(self) -> MenuItem:
        """Get the currently selected menu item."""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None


def create_main_menu() -> Menu:
    """Create the main menu."""
    return Menu(
        "WebDoom - Pygame Edition",
        [
            MenuItem("Start Game"),
            MenuItem("Options"),
            MenuItem("Quit"),
        ],
    )
