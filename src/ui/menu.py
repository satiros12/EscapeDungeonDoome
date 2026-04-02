"""
Menu system for game menus
"""

import pygame
import time
from typing import List, Callable


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
        self.title_color = (255, 200, 50)  # Gold
        self.selected_color = (255, 255, 255)  # White
        self.unselected_color = (120, 120, 130)  # Gray
        self.hover_color = (255, 220, 150)  # Light gold
        self.background_color = (20, 15, 25)  # Dark background
        self.border_color = (100, 80, 60)  # Brown border

    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
                self._play_select_sound()
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
                self._play_select_sound()
            elif event.key == pygame.K_RETURN:
                self._play_enter_sound()
                item = self.items[self.selected_index]
                if item.callback:
                    item.callback()
            elif event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.items)
                self._play_select_sound()
            elif event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.items)
                self._play_select_sound()

    def _play_select_sound(self):
        """Play menu selection sound (placeholder - could add actual sound)."""
        pass

    def _play_enter_sound(self):
        """Play menu enter sound."""
        pass

    def update(self, dt: float):
        """Update menu animations."""
        self.animation_time += dt

        # Animate selected item
        for i, item in enumerate(self.items):
            if i == self.selected_index:
                item.hover_anim = min(1.0, item.hover_anim + dt * 5)
            else:
                item.hover_anim = max(0.0, item.hover_anim - dt * 5)

    def render(self, screen: pygame.Surface) -> None:
        """Render the menu with enhanced visuals."""
        # Draw background
        screen.fill(self.background_color)

        # Draw some atmospheric background elements
        self._draw_background(screen)

        # Render title with glow effect
        self._render_title(screen)

        # Render menu items
        self._render_items(screen)

        # Render controls hint
        self._render_controls_hint(screen)

    def _draw_background(self, screen: pygame.Surface):
        """Draw atmospheric background elements."""
        width = screen.get_width()
        height = screen.get_height()

        # Draw some decorative pillars
        pillar_width = 40
        pillar_gap = 150
        for x in range(0, width, pillar_gap):
            pygame.draw.rect(screen, (30, 25, 35), (x, 0, pillar_width, height))
            # Pillar edge
            pygame.draw.rect(screen, (50, 45, 55), (x, 0, 3, height))
            pygame.draw.rect(screen, (20, 15, 25), (x + pillar_width - 3, 0, 3, height))

        # Floor
        floor_y = height * 3 // 4
        pygame.draw.rect(screen, (40, 30, 25), (0, floor_y, width, height - floor_y))

        # Floor line
        pygame.draw.line(screen, (80, 60, 40), (0, floor_y), (width, floor_y), 3)

    def _render_title(self, screen: pygame.Surface):
        """Render title with effects."""
        width = screen.get_width()

        # Title font
        title_font = pygame.font.Font(None, 56)
        subtitle_font = pygame.font.Font(None, 28)

        # Animated glow effect
        glow_intensity = int(200 + 55 * abs(self.animation_time % 2 - 1))

        # Shadow
        shadow_surf = title_font.render(self.title, True, (50, 40, 30))
        shadow_rect = shadow_surf.get_rect(center=(width // 2 + 3, 103))
        screen.blit(shadow_surf, shadow_rect)

        # Main title with gradient effect (simulated)
        title_surf = title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(width // 2, 100))
        screen.blit(title_surf, title_rect)

        # Subtitle
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

            # Calculate position with slight wave animation
            base_y = start_y + i * self.item_spacing
            wave_offset = int(3 * (self.animation_time % 1)) if is_selected else 0

            # Item background box when selected
            if is_selected:
                box_width = 300
                box_height = 50
                box_x = width // 2 - box_width // 2 + wave_offset
                box_y = base_y - 15

                # Draw selection box
                pygame.draw.rect(
                    screen, (40, 35, 45), (box_x, box_y, box_width, box_height)
                )
                pygame.draw.rect(
                    screen, self.border_color, (box_x, box_y, box_width, box_height), 2
                )

                # Draw selection indicator
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

            # Determine color
            if is_selected:
                color = self.selected_color
                # Add highlight
                highlight = font.render(item.text, True, (255, 255, 200))
            else:
                color = self.unselected_color
                highlight = None

            # Render text
            text_surf = font.render(item.text, True, color)
            text_rect = text_surf.get_rect(center=(width // 2 + wave_offset, base_y))
            screen.blit(text_surf, text_rect)

            # Render highlight (slight glow) when selected
            if highlight:
                highlight.set_alpha(100)
                highlight_rect = highlight.get_rect(
                    center=(width // 2 + wave_offset, base_y)
                )
                screen.blit(highlight, highlight_rect)

    def _render_controls_hint(self, screen: pygame.Surface):
        """Render controls hint at bottom."""
        width = screen.get_height()
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
