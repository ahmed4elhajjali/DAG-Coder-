"""
Shared constants for the Snake game.

Centralises configuration values such as screen dimensions,
colours, frame rate, and other game‑wide settings.
"""

# ---------------------------------------------------------------------------
# Screen settings
# ---------------------------------------------------------------------------
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
WINDOW_TITLE: str = "Snake Game"

# ---------------------------------------------------------------------------
# Game timing
# ---------------------------------------------------------------------------
FPS: int = 15

# ---------------------------------------------------------------------------
# Grid / block size
# ---------------------------------------------------------------------------
BLOCK_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // BLOCK_SIZE

# ---------------------------------------------------------------------------
# Colours (RGB tuples)
# ---------------------------------------------------------------------------
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 30, 30)
COLOR_GREEN = (0, 200, 0)
COLOR_DARK_GREEN = (0, 155, 0)
COLOR_BLUE = (30, 30, 200)
COLOR_GREY = (100, 100, 100)

# Specific colours for game elements
COLOR_SNAKE_HEAD = COLOR_GREEN
COLOR_SNAKE_BODY = COLOR_DARK_GREEN
COLOR_FOOD = COLOR_RED
COLOR_BACKGROUND = COLOR_BLACK
COLOR_TEXT = COLOR_WHITE

# ---------------------------------------------------------------------------
# Direction vectors (x, y) – each step moves one BLOCK_SIZE
# ---------------------------------------------------------------------------
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Mapping for convenience when handling key input
DIRECTION_VECTORS = {
    "UP": UP,
    "DOWN": DOWN,
    "LEFT": LEFT,
    "RIGHT": RIGHT,
}

# ---------------------------------------------------------------------------
# Miscellaneous game settings
# ---------------------------------------------------------------------------
INITIAL_SNAKE_LENGTH: int = 5
MAX_FOOD_COUNT: int = 1

# Font settings – used by the UI module
FONT_NAME: str = "freesansbold.ttf"
FONT_SIZE: int = 24
