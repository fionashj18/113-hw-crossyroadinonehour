"""
Crossy Road - 2D Python Game
==============================
A classic Crossy Road clone built with Pygame.
Move your chicken across busy roads and a river to reach the other side!

Requirements:
    pip install pygame

Controls:
    W / Up Arrow    -> Move Up
    A / Left Arrow  -> Move Left
    D / Right Arrow -> Move Right
    S / Down Arrow  -> Move Down
    R               -> Restart (after game over)
    Q / ESC         -> Quit

GitHub: https://github.com/fionashj18/113-hw-crossyroadinonehour
"""

import sys
import pygame

from settings import *
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Crossy Road")
    clock = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()