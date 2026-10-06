"""
snake package – core Snake implementation.

The ``Snake`` class encapsulates movement, growth, collision detection,
and rendering using *pygame*.
"""

from __future__ import annotations

from typing import List, Tuple

import pygame

from constants import (
    BLOCK_SIZE,
    COLOR_SNAKE_BODY,
    COLOR_SNAKE_HEAD,
    GRID_HEIGHT,
    GRID_WIDTH,
    INITIAL_SNAKE_LENGTH,
    UP,
    DOWN,
    LEFT,
    RIGHT,
)

# ---------------------------------------------------------------------------
# Helper type aliases
# ---------------------------------------------------------------------------
GridPos = Tuple[int, int]   # (column, row) on the logical grid


class Snake:
    """Represents the player's snake."""

    @staticmethod
    def _initial_body() -> List[GridPos]:
        """Create the initial body centred on the screen, facing RIGHT."""
        head_x = GRID_WIDTH // 2
        head_y = GRID_HEIGHT // 2
        return [(head_x - i, head_y) for i in range(INITIAL_SNAKE_LENGTH)]

    def __init__(self) -> None:
        self.body: List[GridPos] = self._initial_body()
        self.direction: GridPos = RIGHT
        self._grow_pending: int = 0

    # -----------------------------------------------------------------------
    # Movement & growth
    # -----------------------------------------------------------------------
    def set_direction(self, new_direction: GridPos) -> None:
        """Change heading; 180° turns are ignored."""
        opposite = (self.direction[0] * -1, self.direction[1] * -1)
        if new_direction != opposite:
            self.direction = new_direction

    def grow(self, amount: int = 1) -> None:
        """Queue *amount* extra segments to be added on subsequent moves."""
        self._grow_pending += max(0, amount)

    def move(self) -> None:
        """Advance the snake one step in the current direction."""
        dx, dy = self.direction
        head_x, head_y = self.body[0]
        new_head: GridPos = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)

        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self.body.pop()

    # -----------------------------------------------------------------------
    # Collision detection
    # -----------------------------------------------------------------------
    def collides_with_wall(self) -> bool:
        """Return True if the head is outside the playable grid."""
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

    def collides_with_self(self) -> bool:
        """Return True if the head touches any other body segment."""
        head = self.body[0]
        return head in self.body[1:]

    # -----------------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        """Render the snake onto *surface*."""
        # Head
        head_rect = pygame.Rect(
            self.body[0][0] * BLOCK_SIZE,
            self.body[0][1] * BLOCK_SIZE,
            BLOCK_SIZE,
            BLOCK_SIZE,
        )
        pygame.draw.rect(surface, COLOR_SNAKE_HEAD, head_rect)

        # Body
        for segment in self.body[1:]:
            seg_rect = pygame.Rect(
                segment[0] * BLOCK_SIZE,
                segment[1] * BLOCK_SIZE,
                BLOCK_SIZE,
                BLOCK_SIZE,
            )
            pygame.draw.rect(surface, COLOR_SNAKE_BODY, seg_rect)

    # -----------------------------------------------------------------------
    # Utility helpers
    # -----------------------------------------------------------------------
    def get_head_position(self) -> GridPos:
        """Return the head coordinates."""
        return self.body[0]

    def reset(self) -> None:
        """Restore the snake to its initial state (useful after a game over)."""
        self.body = self._initial_body()
        self.direction = RIGHT
        self._grow_pending = 0

    # -----------------------------------------------------------------------
    # Debug representation
    # -----------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Snake head={self.body[0]} length={len(self.body)}>"
