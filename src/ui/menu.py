"""
Menu system for game menus
"""

import pygame
import time
import os
from typing import List, Callable, Optional


class MenuItem:
    """Represents a single menu item."""

    def __init__(self, text: str, callback: Callable = None):
        self.text = text
        self.callback = callback
        self.hover_anim = 0.0


class Menu:
    """Enhanced menu system with better visuals."""

    def __init__(self, title: str, items: List[MenuItem]):
        self.title = title
        self.items = items
        self.selected_index = 0
        self.font_size = 40
        self.item_spacing = 60
        self.animation_time = 0

        # Colors
        self.title_color = (255, 200, 50)
        self.selected_color = (255, 255, 255)
        self.unselected_color = (120, 120, 130)
        self.hover_color = (255, 220, 150)
        self.background_color = (20, 15, 25)
        self.border_color = (100, 80, 60)

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
            elif event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.items)

    def update(self, dt: float):
        """Update menu animations."""
        self.animation_time += dt

        for i, item in enumerate(self.items):
            if i == self.selected_index:
                item.hover_anim = min(1.0, item.hover_anim + dt * 5)
            else:
                item.hover_anim = max(0.0, item.hover_anim - dt * 5)

    def render(self, screen: pygame.Surface) -> None:
        """Render the menu with enhanced visuals."""
        screen.fill(self.background_color)
        self._draw_background(screen)
        self._render_title(screen)
        self._render_items(screen)
        self._render_controls_hint(screen)

    def _draw_background(self, screen: pygame.Surface):
        """Draw atmospheric background elements."""
        width = screen.get_width()
        height = screen.get_height()

        for x in range(0, width, 150):
            pygame.draw.rect(screen, (30, 25, 35), (x, 0, 40, height))
            pygame.draw.rect(screen, (50, 45, 55), (x, 0, 3, height))
            pygame.draw.rect(screen, (20, 15, 25), (x + 37, 0, 3, height))

        floor_y = height * 3 // 4
        pygame.draw.rect(screen, (40, 30, 25), (0, floor_y, width, height - floor_y))
        pygame.draw.line(screen, (80, 60, 40), (0, floor_y), (width, floor_y), 3)

    def _render_title(self, screen: pygame.Surface):
        """Render title with effects."""
        width = screen.get_width()

        title_font = pygame.font.Font(None, 56)
        subtitle_font = pygame.font.Font(None, 28)

        glow_intensity = int(200 + 55 * abs(self.animation_time % 2 - 1))

        shadow_surf = title_font.render(self.title, True, (50, 40, 30))
        shadow_rect = shadow_surf.get_rect(center=(width // 2 + 3, 103))
        screen.blit(shadow_surf, shadow_rect)

        title_surf = title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(width // 2, 100))
        screen.blit(title_surf, title_rect)

        subtitle = "A DOOM-style Dungeon Crawler"
        sub_surf = subtitle_font.render(subtitle, True, (150, 140, 130))
        sub_rect = sub_surf.get_rect(center=(width // 2, 140))
        screen.blit(sub_surf, sub_rect)

    def _render_items(self, screen: pygame.Surface):
        """Render menu items with selection effects."""
        width = screen.get_width()
        font = pygame.font.Font(None, self.font_size)

        start_y = 250

        for i, item in enumerate(self.items):
            is_selected = i == self.selected_index

            base_y = start_y + i * self.item_spacing
            wave_offset = int(3 * (self.animation_time % 1)) if is_selected else 0

            if is_selected:
                box_width = 300
                box_height = 50
                box_x = width // 2 - box_width // 2 + wave_offset
                box_y = base_y - 15

                pygame.draw.rect(
                    screen, (40, 35, 45), (box_x, box_y, box_width, box_height)
                )
                pygame.draw.rect(
                    screen, self.border_color, (box_x, box_y, box_width, box_height), 2
                )

                indicator_size = 10
                pygame.draw.polygon(
                    screen,
                    (255, 200, 50),
                    [
                        (box_x - 20, box_y + box_height // 2),
                        (
                            box_x - 20 - indicator_size,
                            box_y + box_height // 2 - indicator_size // 2,
                        ),
                        (
                            box_x - 20 - indicator_size,
                            box_y + box_height // 2 + indicator_size // 2,
                        ),
                    ],
                )
                pygame.draw.polygon(
                    screen,
                    (255, 200, 50),
                    [
                        (box_x + box_width + 20, box_y + box_height // 2),
                        (
                            box_x + box_width + 20 + indicator_size,
                            box_y + box_height // 2 - indicator_size // 2,
                        ),
                        (
                            box_x + box_width + 20 + indicator_size,
                            box_y + box_height // 2 + indicator_size // 2,
                        ),
                    ],
                )

            if is_selected:
                color = self.selected_color
                highlight = font.render(item.text, True, (255, 255, 200))
            else:
                color = self.unselected_color
                highlight = None

            text_surf = font.render(item.text, True, color)
            text_rect = text_surf.get_rect(center=(width // 2 + wave_offset, base_y))
            screen.blit(text_surf, text_rect)

            if highlight:
                highlight.set_alpha(100)
                highlight_rect = highlight.get_rect(
                    center=(width // 2 + wave_offset, base_y)
                )
                screen.blit(highlight, highlight_rect)

    def _render_controls_hint(self, screen: pygame.Surface):
        """Render controls hint at bottom."""
        font = pygame.font.Font(None, 22)

        hint_text = "W/S or UP/DOWN to select | ENTER to confirm"
        hint_surf = font.render(hint_text, True, (100, 100, 110))
        hint_rect = hint_surf.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 40)
        )
        screen.blit(hint_surf, hint_rect)

    def get_selected_item(self) -> MenuItem:
        """Get the currently selected menu item."""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None


class OptionsMenu(Menu):
    """Options menu with map selection."""

    def __init__(self, current_map: str, on_map_change: Callable):
        self.current_map = current_map
        self.on_map_change = on_map_change
        self.maps = self._get_available_maps()
        self.selected_map_index = (
            self.maps.index(current_map) if current_map in self.maps else 0
        )

        # Create items for each map
        items = [MenuItem(f"MAP: {m}") for m in self.maps]
        items.append(MenuItem("BACK"))

        super().__init__("OPTIONS", items)

    def _get_available_maps(self) -> List[str]:
        """Get list of available maps."""
        maps_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "maps"
        )
        if os.path.exists(maps_dir):
            return [
                f.replace(".json", "")
                for f in os.listdir(maps_dir)
                if f.endswith(".json")
            ]
        return ["base", "arena", "maze"]

    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                if self.selected_index < len(self.maps):
                    # Selected a map
                    selected_map = self.maps[self.selected_index]
                    if selected_map != self.current_map:
                        self.current_map = selected_map
                        self.on_map_change(selected_map)
                else:
                    # Back - do nothing, let game handle it
                    pass
            elif event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.items)

    def render(self, screen: pygame.Surface) -> None:
        """Render options menu."""
        screen.fill(self.background_color)

        width = screen.get_width()

        # Title
        title_font = pygame.font.Font(None, 48)
        title_surf = title_font.render("SELECT MAP", True, self.title_color)
        title_rect = title_surf.get_rect(center=(width // 2, 80))
        screen.blit(title_surf, title_rect)

        # Render map options
        font = pygame.font.Font(None, 36)
        start_y = 180

        for i, item in enumerate(self.items):
            is_selected = i == self.selected_index
            base_y = start_y + i * 50

            if is_selected:
                box_width = 250
                box_height = 40
                box_x = width // 2 - box_width // 2
                box_y = base_y - 12

                pygame.draw.rect(
                    screen, (40, 35, 45), (box_x, box_y, box_width, box_height)
                )
                pygame.draw.rect(
                    screen, self.border_color, (box_x, box_y, box_width, box_height), 2
                )

            # Mark current map
            if i < len(self.maps) and self.maps[i] == self.current_map:
                text = f"> {self.maps[i]} (current)"
            elif i == len(self.maps):
                text = "< BACK"
            else:
                text = "  " + self.items[i].text

            color = self.selected_color if is_selected else self.unselected_color
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(width // 2, base_y))
            screen.blit(text_surf, text_rect)

        # Controls hint
        font_hint = pygame.font.Font(None, 22)
        hint_text = "W/S to navigate | ENTER to select"
        hint_surf = font_hint.render(hint_text, True, (100, 100, 110))
        hint_rect = hint_surf.get_rect(center=(width // 2, screen.get_height() - 40))
        screen.blit(hint_surf, hint_rect)


def create_main_menu() -> Menu:
    """Create the main menu."""
    return Menu(
        "WEBDOOM",
        [
            MenuItem("START GAME"),
            MenuItem("OPTIONS"),
            MenuItem("QUIT"),
        ],
    )
