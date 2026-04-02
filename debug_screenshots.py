"""
Game screenshot script for debugging - takes screenshots at intervals
"""

import pygame
import sys
import os
import time
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


def run_game_with_screenshots():
    """Run game and take screenshots."""
    from game import Game

    pygame.init()

    # Create game
    game = Game()

    # Screenshot counter
    screenshot_count = 0
    max_screenshots = 10

    def take_screenshot(name):
        nonlocal screenshot_count
        screenshot_count += 1
        filename = f"screenshots/{screenshot_count:02d}_{name}.png"
        pygame.image.save(game.screen, filename)
        print(f"Screenshot: {filename}")

    print("Starting game loop with screenshots...")

    # Run for limited time
    start_time = time.time()
    frame = 0

    while game.running and time.time() - start_time < 8:
        # Calculate delta time
        dt = game.clock.tick(60) / 1000.0
        frame += 1

        # Handle events
        game._handle_events()

        # Update
        game._update(dt)

        # Render
        game._render()

        # Take screenshots at specific frames
        if frame == 1:
            take_screenshot("01_start")
        elif frame == 30:
            take_screenshot("02_menu_30fps")
        elif frame == 60:
            # Press down arrow to move menu selection
            print("Simulating DOWN key for menu...")
            # Create a mock event
            down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            game._handle_menu_events(down_event)
            take_screenshot("03_menu_down")
        elif frame == 90:
            take_screenshot("04_menu_90fps")
        elif frame == 120:
            # Press enter to start game
            print("Simulating ENTER to start game...")
            enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
            game._handle_menu_events(enter_event)
            take_screenshot("05_enter_pressed")
        elif frame == 180:
            take_screenshot("06_playing")
        elif frame == 240:
            take_screenshot("07_playing_4s")
        elif frame == 300:
            take_screenshot("08_playing_5s")

    take_screenshot("09_final")

    pygame.quit()
    print("Done! Check screenshots folder.")
    print(f"Game state at end: {game.game_engine.state.game_state}")


if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)
    run_game_with_screenshots()
