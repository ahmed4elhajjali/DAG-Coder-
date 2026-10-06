"""
food package – simple food object for the Snake game.

The ``Food`` class handles random placement (avoiding occupied cells),
eating detection, and drawing itself onto a pygame surface.
"""

from __future__ import annotations

import random
from typing import Iterable, Tuple

import pygame

import constants

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
GridPos = Tuple[int, int]          # (grid_x, grid_y)
PixelRect = pygame.Rect           # rectangle in pixel coordinates


class Food:
    """Represents a single piece of food on the board."""

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface: pygame.Surface = surface
        self.block_size: int = constants.BLOCK_SIZE
        self.color = constants.COLOR_FOOD
        # Initial spawn – no need to avoid anything yet
        self.position: GridPos = self._random_position()

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------
    def _random_position(self, occupied: Iterable[GridPos] | None = None) -> GridPos:
        """
        Return a random grid coordinate not present in *occupied*.
        """
        max_x = constants.GRID_WIDTH - 1
        max_y = constants.GRID_HEIGHT - 1
        occupied_set = set(occupied) if occupied is not None else set()

        while True:
            pos = (random.randint(0, max_x), random.randint(0, max_y))
            if pos not in occupied_set:
                return pos

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------
    def spawn(self, occupied_positions: Iterable[GridPos]) -> None:
        """Re‑position the food on a free cell, avoiding *occupied_positions*."""
        self.position = self._random_position(occupied_positions)

    def is_eaten(self, snake_head: GridPos) -> bool:
        """Return True if the snake's head is on the same cell as the food."""
        return self.position == snake_head

    def draw(self) -> None:
        """Render the food onto the stored surface."""
        rect: PixelRect = pygame.Rect(
            self.position[0] * self.block_size,
            self.position[1] * self.block_size,
            self.block_size,
            self.block_size,
        )
        pygame.draw.rect(self.surface, self.color, rect)

    # -----------------------------------------------------------------------
    # Debug representation
    # -----------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"<Food pos={self.position} color={self.color}>"
