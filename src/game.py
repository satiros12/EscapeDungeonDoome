"""
Game facade - coordinates all game components
"""

import pygame


class Game:
    """Main game class that coordinates all systems."""

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("WebDoom - Pygame Edition")
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(60)

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def _update(self):
        """Update game state."""
        pass

    def _render(self):
        """Render the game."""
        self.screen.fill((0, 0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    import pygame

    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
