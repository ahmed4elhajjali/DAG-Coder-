#!/usr/bin/env python3
"""
Main entry point for the Snake game.

Sets up pygame, creates the core ``Snake`` and ``Food`` objects,
runs the main loop, processes input, updates the game state,
renders everything, and persists the high score.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

from constants import (
    BLOCK_SIZE,
    COLOR_BACKGROUND,
    COLOR_TEXT,
    FONT_NAME,
    FONT_SIZE,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
    UP,
    DOWN,
    LEFT,
    RIGHT,
)
from food import Food
from highscore import read_high_score, update_high_score
from snake import Snake


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    font: pygame.font.Font,
    colour: tuple[int, int, int] = COLOR_TEXT,
) -> None:
    """Render *text* at *pos* (top‑left corner) onto *surface*."""
    img = font.render(text, True, colour)
    surface.blit(img, pos)


def _handle_key(event_key: int, snake: Snake) -> None:
    """Map pygame key constants to direction vectors and update the snake."""
    if event_key == pygame.K_UP:
        snake.set_direction(UP)
    elif event_key == pygame.K_DOWN:
        snake.set_direction(DOWN)
    elif event_key == pygame.K_LEFT:
        snake.set_direction(LEFT)
    elif event_key == pygame.K_RIGHT:
        snake.set_direction(RIGHT)
    elif event_key == pygame.K_ESCAPE:
        pygame.event.post(pygame.event.Event(pygame.QUIT))


# ---------------------------------------------------------------------------
# Core game loop
# ---------------------------------------------------------------------------
def main() -> None:
    """Initialise pygame and run the Snake game loop."""
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Font for score / high‑score display
    try:
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
    except FileNotFoundError:
        font = pygame.font.SysFont(None, FONT_SIZE)

    # Persistent high‑score file (saved next to this script)
    highscore_path = Path(__file__).with_name("highscore.json")
    high_score = read_high_score(highscore_path)

    # Game objects
    snake = Snake()
    food = Food(screen)
    food.spawn(snake.body)  # ensure first food is not on the snake

    score = 0
    running = True

    while running:
        # -------------------------------------------------------------------
        # Event handling
        # -------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                _handle_key(event.key, snake)

        if not running:
            break

        # -------------------------------------------------------------------
        # Game logic – move snake
        # -------------------------------------------------------------------
        snake.move()

        # Collision with walls or self → game over
        if snake.collides_with_wall() or snake.collides_with_self():
            high_score = update_high_score(highscore_path, score)
            pygame.time.delay(1000)          # brief pause before reset
            snake.reset()
            food.spawn(snake.body)
            score = 0
            continue  # skip rendering this frame

        # -------------------------------------------------------------------
        # Food handling
        # -------------------------------------------------------------------
        if food.is_eaten(snake.get_head_position()):
            snake.grow()
            score += 1
            food.spawn(snake.body)

        # -------------------------------------------------------------------
        # Rendering
        # -------------------------------------------------------------------
        screen.fill(COLOR_BACKGROUND)

        food.draw()
        snake.draw(screen)

        _draw_text(screen, f"Score: {score}", (10, 10), font)
        _draw_text(screen, f"High Score: {high_score}", (10, 30 + FONT_SIZE), font)

        pygame.display.flip()
        clock.tick(FPS)

    # -----------------------------------------------------------------------
    # Clean‑up
    # -----------------------------------------------------------------------
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
