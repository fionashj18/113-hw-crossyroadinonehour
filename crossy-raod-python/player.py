"""
player.py – The player's chicken character
"""

import pygame
from settings import (
    GRID_SIZE, PLAYER_SIZE, PLAYER_MOVE_DIST, STEP_DURATION, MOVE_COOLDOWN,
    SCREEN_WIDTH, ROWS,
    C_CHICKEN, C_CHICKEN_BEAK, C_CHICKEN_EYE, C_CHICKEN_LEG,
)


class Player:
    def __init__(self):
        self.reset()

    # ── public state ──────────────────────────────────────
    def reset(self):
        # Grid position (col, row).  Row 0 = bottom lane.
        self.col = 5
        self.row = 0

        # Pixel target & current (for smooth animation)
        self._target_x, self._target_y = self._grid_to_px(self.col, self.row)
        self.px = self._target_x
        self.py = self._target_y

        # Animation / input cooldown
        self._moving        = False
        self._move_timer    = 0.0
        self._cooldown_left = 0.0

        # Direction the chicken is facing (for beak/eye)
        self.facing = "up"   # up | down | left | right

        # Track highest row reached (for scoring)
        self.max_row = 0

    # ── movement API ──────────────────────────────────────
    def request_move(self, direction: str):
        """Called by Game when the player presses a direction key."""
        if self._moving or self._cooldown_left > 0:
            return

        dx, dy = {"up": (0, 1), "down": (0, -1),
                  "left": (-1, 0), "right": (1, 0)}[direction]

        new_col = self.col + dx
        new_row = self.row + dy

        # Clamp horizontally; allow vertical 0..ROWS-1
        if new_col < 0 or new_col >= SCREEN_WIDTH // GRID_SIZE:
            return
        if new_row < 0 or new_row >= ROWS:
            return

        self.col = new_col
        self.row = new_row
        self.facing = direction
        self._target_x, self._target_y = self._grid_to_px(self.col, self.row)
        self._moving     = True
        self._move_timer = 0.0

        if self.row > self.max_row:
            self.max_row = self.row

    # ── update ────────────────────────────────────────────
    def update(self, dt: float):
        if self._cooldown_left > 0:
            self._cooldown_left -= dt

        if self._moving:
            self._move_timer += dt
            t = min(self._move_timer / STEP_DURATION, 1.0)
            # Ease-out quad
            t_ease = 1 - (1 - t) ** 2

            start_x = self._target_x - (self.col - (self.col - (1 if self.facing == "right" else -1 if self.facing == "left" else 0))) * GRID_SIZE
            start_y = self._target_y + (1 if self.facing == "up" else -1 if self.facing == "down" else 0) * GRID_SIZE

            # Simpler: lerp from previous pixel pos saved at move start
            self.px += (self._target_x - self.px) * min(dt / max(STEP_DURATION - self._move_timer + dt, 0.001), 1.0)
            self.py += (self._target_y - self.py) * min(dt / max(STEP_DURATION - self._move_timer + dt, 0.001), 1.0)

            if t >= 1.0:
                self.px = self._target_x
                self.py = self._target_y
                self._moving        = False
                self._cooldown_left = MOVE_COOLDOWN

    # ── collision ─────────────────────────────────────────
    def get_rect(self) -> pygame.Rect:
        cx = self.px + GRID_SIZE // 2
        cy = self.py + GRID_SIZE // 2
        return pygame.Rect(
            cx - PLAYER_SIZE // 2,
            cy - PLAYER_SIZE // 2,
            PLAYER_SIZE,
            PLAYER_SIZE,
        )

    # ── drawing ───────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        cx = int(self.px + GRID_SIZE // 2)
        cy = int(self.py + GRID_SIZE // 2)
        s = PLAYER_SIZE

        # Body (oval-ish)
        body_rect = pygame.Rect(cx - s // 2, cy - s // 2 + 2, s, s - 4)
        pygame.draw.ellipse(surface, C_CHICKEN, body_rect)
        pygame.draw.ellipse(surface, (200, 180, 140), body_rect, 2)

        # Head
        head_r = s // 4
        hx, hy = cx, cy - s // 2 - head_r + 6
        pygame.draw.circle(surface, C_CHICKEN, (hx, hy), head_r)
        pygame.draw.circle(surface, (200, 180, 140), (hx, hy), head_r, 2)

        # Eye
        eye_offset = {"up": (2, -2), "down": (-2, 2),
                      "left": (-3, 0), "right": (3, 0)}
        eox, eoy = eye_offset.get(self.facing, (2, -2))
        pygame.draw.circle(surface, C_CHICKEN_EYE, (hx + eox, hy + eoy), 3)
        # Highlight
        pygame.draw.circle(surface, (255, 255, 255), (hx + eox + 1, hy + eoy - 1), 1)

        # Beak
        beak_offset = {"up": (0, -head_r - 2), "down": (0, head_r + 2),
                       "left": (-head_r - 2, 0), "right": (head_r + 2, 0)}
        box, boy = beak_offset.get(self.facing, (0, -head_r - 2))
        bx, by = hx + box, hy + boy
        beak_points = {
            "up":    [(bx - 3, by), (bx + 3, by), (bx, by - 5)],
            "down":  [(bx - 3, by), (bx + 3, by), (bx, by + 5)],
            "left":  [(bx, by - 3), (bx, by + 3), (bx - 5, by)],
            "right": [(bx, by - 3), (bx, by + 3), (bx + 5, by)],
        }
        pygame.draw.polygon(surface, C_CHICKEN_BEAK, beak_points[self.facing])

        # Legs
        leg_y = cy + s // 2 - 2
        pygame.draw.line(surface, C_CHICKEN_LEG, (cx - 5, leg_y), (cx - 5, leg_y + 6), 3)
        pygame.draw.line(surface, C_CHICKEN_LEG, (cx + 5, leg_y), (cx + 5, leg_y + 6), 3)

    # ── helpers ───────────────────────────────────────────
    @staticmethod
    def _grid_to_px(col, row):
        """Convert grid (col, row) to top-left pixel of that tile.
           Row 0 is at the BOTTOM of the screen."""
        x = col * GRID_SIZE
        y = (ROWS - 1 - row) * GRID_SIZE
        return x, y