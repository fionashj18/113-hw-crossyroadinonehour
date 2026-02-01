"""
settings.py – Global constants for Crossy Road
"""

# ─── Display ─────────────────────────────────────────────
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 720
FPS           = 60
GRID_SIZE     = 60          # pixel size of one tile

COLS = SCREEN_WIDTH  // GRID_SIZE   # 10 columns  (rounded)
ROWS = SCREEN_HEIGHT // GRID_SIZE   # 12 rows     (rounded)

# ─── Colours (R, G, B) ──────────────────────────────────
C_BG           = (34,  139, 34)   # grass green
C_GRASS_DARK   = (28,  120, 28)
C_ROAD         = (60,  60,  60)
C_ROAD_LINE    = (240, 220, 50)
C_SIDEWALK     = (180, 170, 150)
C_RIVER        = (40,  100, 200)
C_RIVER_DARK   = (30,  80,  170)
C_TREE         = (34,  100, 10)
C_TREE_TRUNK   = (90,  60,  30)
C_FLOWER_RED   = (220, 40,  40)
C_FLOWER_PINK  = (230, 100, 150)
C_CAR_RED      = (200, 30,  30)
C_CAR_BLUE     = (30,  60,  200)
C_CAR_YELLOW   = (230, 200, 30)
C_CAR_WHITE    = (240, 240, 240)
C_LOG          = (120, 70,  30)
C_LOG_DARK     = (90,  50,  20)
C_CHICKEN      = (240, 220, 180)
C_CHICKEN_BEAK = (230, 160, 30)
C_CHICKEN_EYE  = (20,  20,  20)
C_CHICKEN_LEG  = (200, 160, 60)
C_TEXT         = (255, 255, 255)
C_TEXT_SHADOW  = (0,   0,   0)
C_OVERLAY      = (0,   0,   0, 160)
C_STAR         = (255, 215, 0)
C_WIN_BG       = (30,  30,  60)

# ─── Player ──────────────────────────────────────────────
PLAYER_SIZE      = 40          # bounding box in pixels
PLAYER_MOVE_DIST = GRID_SIZE   # how far one step moves the player
STEP_DURATION    = 0.12        # seconds to animate one step
MOVE_COOLDOWN    = 0.05        # minimum time between new move inputs

# ─── Lane layout (bottom → top, row 0 = bottom of screen) ───
# Each entry: (type, speed, direction)
#   type      – "grass" | "road" | "river" | "sidewalk"
#   speed     – pixels/sec for cars/logs (0 for static)
#   direction –  1 = left-to-right,  -1 = right-to-left
LANE_DEFS = [
    # row  0 – bottom safe grass
    ("sidewalk",  0,  1),
    ("grass",     0,  1),
    # rows 2-3 – first road section
    ("road",  180, -1),
    ("road",  220,  1),
    # row  4 – grass breather
    ("grass",     0,  1),
    # rows 5-6 – second road section
    ("road",  200,  1),
    ("road",  250, -1),
    # row  7 – river
    ("river", 130,  1),
    # row  8 – grass breather
    ("grass",     0,  1),
    # rows 9-10 – third road section
    ("road",  190, -1),
    ("road",  240,  1),
    # row 11 – top safe grass / goal
    ("grass",     0,  1),
]

# ─── Cars ────────────────────────────────────────────────
CAR_WIDTH      = 100          # pixels
CAR_HEIGHT     = 42
CAR_COLORS     = [C_CAR_RED, C_CAR_BLUE, C_CAR_YELLOW, C_CAR_WHITE]
CAR_SPAWN_INTERVAL_MIN = 1.2  # seconds
CAR_SPAWN_INTERVAL_MAX = 2.8

# ─── Logs ────────────────────────────────────────────────
LOG_WIDTH      = 120
LOG_HEIGHT     = 40
LOG_SPAWN_INTERVAL_MIN = 1.5
LOG_SPAWN_INTERVAL_MAX = 3.0

# ─── Decorations ─────────────────────────────────────────
TREE_CHANCE    = 0.12         # probability per grass tile
FLOWER_CHANCE  = 0.18

# ─── Scoring ─────────────────────────────────────────────
SCORE_PER_ROW     = 10
SCORE_WIN_BONUS   = 50
TIME_PENALTY_PER_SEC = 0.3    # score drains over time