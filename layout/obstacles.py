"""
obstacles.py – Cars and Logs that move across lanes
"""

import random
import pygame
from settings import (
    SCREEN_WIDTH, GRID_SIZE, ROWS,
    CAR_WIDTH, CAR_HEIGHT, CAR_COLORS,
    CAR_SPAWN_INTERVAL_MIN, CAR_SPAWN_INTERVAL_MAX,
    LOG_WIDTH, LOG_HEIGHT,
    LOG_SPAWN_INTERVAL_MIN, LOG_SPAWN_INTERVAL_MAX,
    C_LOG, C_LOG_DARK,
)


# ─── Car ──────────────────────────────────────────────────
class Car:
    def __init__(self, row: int, direction: int, speed: float):
        self.row       = row
        self.direction = direction   # +1 or -1
        self.speed     = speed
        self.color     = random.choice(CAR_COLORS)
        self.w         = CAR_WIDTH
        self.h         = CAR_HEIGHT

        # Start off-screen on the appropriate side
        if direction == 1:   # moving right → start left
            self.x = -self.w - random.randint(0, 60)
        else:                # moving left  → start right
            self.x = SCREEN_WIDTH + random.randint(0, 60)

        # Vertical centre of the lane
        self.y = (ROWS - 1 - row) * GRID_SIZE + (GRID_SIZE - self.h) // 2

    def update(self, dt: float):
        self.x += self.direction * self.speed * dt

    def is_off_screen(self) -> bool:
        if self.direction == 1:
            return self.x > SCREEN_WIDTH + 20
        return self.x < -self.w - 20

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), self.y, self.w, self.h)

    def draw(self, surface: pygame.Surface):
        r = self.get_rect()
        # Body
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        # Darker outline
        darker = tuple(max(c - 40, 0) for c in self.color)
        pygame.draw.rect(surface, darker, r, 2, border_radius=6)

        # Windshield
        wind_margin = 12
        wind_rect = pygame.Rect(
            r.x + wind_margin,
            r.y + 4,
            r.w - wind_margin * 2,
            r.h - 12,
        )
        pygame.draw.rect(surface, (150, 210, 240), wind_rect, border_radius=3)
        pygame.draw.rect(surface, (100, 170, 200), wind_rect, 1, border_radius=3)

        # Wheels
        wheel_r = 6
        wheel_y = r.bottom - wheel_r
        for wx in (r.x + 14, r.right - 14):
            pygame.draw.circle(surface, (40, 40, 40), (wx, wheel_y), wheel_r)
            pygame.draw.circle(surface, (80, 80, 80), (wx, wheel_y), wheel_r - 2)

        # Headlights / taillights
        light_color = (255, 240, 180) if self.direction == 1 else (200, 40, 40)
        back_color  = (200, 40, 40)   if self.direction == 1 else (255, 240, 180)
        lx = r.right - 4 if self.direction == 1 else r.x + 4
        bx = r.x + 4     if self.direction == 1 else r.right - 4
        pygame.draw.rect(surface, light_color, (lx - 3, r.y + 8, 5, 8), border_radius=2)
        pygame.draw.rect(surface, back_color,  (bx - 2, r.y + 8, 4, 8), border_radius=2)


# ─── Log ──────────────────────────────────────────────────
class Log:
    def __init__(self, row: int, direction: int, speed: float):
        self.row       = row
        self.direction = direction
        self.speed     = speed
        self.w         = LOG_WIDTH + random.randint(-20, 30)
        self.h         = LOG_HEIGHT

        if direction == 1:
            self.x = -self.w - random.randint(0, 80)
        else:
            self.x = SCREEN_WIDTH + random.randint(0, 80)

        self.y = (ROWS - 1 - row) * GRID_SIZE + (GRID_SIZE - self.h) // 2

    def update(self, dt: float):
        self.x += self.direction * self.speed * dt

    def is_off_screen(self) -> bool:
        if self.direction == 1:
            return self.x > SCREEN_WIDTH + 20
        return self.x < -self.w - 20

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), self.y, self.w, self.h)

    def draw(self, surface: pygame.Surface):
        r = self.get_rect()
        # Main log body (rounded rect)
        pygame.draw.rect(surface, C_LOG, r, border_radius=r.h // 2)
        pygame.draw.rect(surface, C_LOG_DARK, r, 3, border_radius=r.h // 2)

        # End caps (circles)
        cap_r = r.h // 2
        pygame.draw.circle(surface, C_LOG,      (r.x + cap_r, r.centery), cap_r)
        pygame.draw.circle(surface, C_LOG_DARK, (r.x + cap_r, r.centery), cap_r, 2)
        pygame.draw.circle(surface, C_LOG,      (r.right - cap_r, r.centery), cap_r)
        pygame.draw.circle(surface, C_LOG_DARK, (r.right - cap_r, r.centery), cap_r, 2)

        # Bark lines
        line_color = (80, 45, 15)
        for i in range(3):
            lx = r.x + cap_r + 15 + i * (r.w - cap_r * 2 - 15) // 3
            pygame.draw.line(surface, line_color, (lx, r.y + 6), (lx + 4, r.bottom - 6), 2)


# ─── Spawner ──────────────────────────────────────────────
class ObstacleSpawner:
    """Manages spawning timers for one lane."""

    def __init__(self, row: int, lane_type: str, speed: float, direction: int):
        self.row       = row
        self.lane_type = lane_type   # "road" or "river"
        self.speed     = speed
        self.direction = direction

        if lane_type == "road":
            self._interval_min = CAR_SPAWN_INTERVAL_MIN
            self._interval_max = CAR_SPAWN_INTERVAL_MAX
        else:
            self._interval_min = LOG_SPAWN_INTERVAL_MIN
            self._interval_max = LOG_SPAWN_INTERVAL_MAX

        self._timer = random.uniform(0, self._interval_max)  # stagger first spawn

    def update(self, dt: float, obstacle_list: list):
        self._timer -= dt
        if self._timer <= 0:
            if self.lane_type == "road":
                obstacle_list.append(Car(self.row, self.direction, self.speed))
            else:
                obstacle_list.append(Log(self.row, self.direction, self.speed))
            self._timer = random.uniform(self._interval_min, self._interval_max)