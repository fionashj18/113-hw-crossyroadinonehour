"""
game.py – Main game logic, state machine, collision, scoring
"""

import pygame
from enum import Enum, auto

from settings import (
    LANE_DEFS, ROWS, GRID_SIZE, SCREEN_WIDTH,
    SCORE_PER_ROW, SCORE_WIN_BONUS, TIME_PENALTY_PER_SEC,
)
from player import Player
from obstacles import ObstacleSpawner, Car, Log
from background import Background
from ui import UI


class State(Enum):
    START   = auto()
    PLAYING = auto()
    DEAD    = auto()
    WIN     = auto()


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background = Background()
        self.ui = UI()

        # Persistent across restarts
        self.best_score = 0

        # One-time init
        self._blink_timer = 0.0
        self._blink_on    = True

        self.state = State.START
        self._init_play()

    # ── setup / reset ─────────────────────────────────────
    def _init_play(self):
        self.player  = Player()
        self.obstacles = []   # list of Car | Log

        # Create one spawner per moving lane
        self.spawners = []
        for row_idx, (ltype, speed, direction) in enumerate(LANE_DEFS):
            if ltype in ("road", "river"):
                self.spawners.append(
                    ObstacleSpawner(row_idx, ltype, speed, direction)
                )

        self.score       = 0.0
        self._prev_max   = 0   # to award row-advance points
        self._river_grace = 0.0  # grace timer: don't drown for a short window after stepping onto river

    # ── event handling ────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if self.state == State.START:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                    import sys; sys.exit()
                self.state = State.PLAYING
                self._init_play()
                return

            if self.state in (State.DEAD, State.WIN):
                if event.key == pygame.K_r:
                    self.state = State.PLAYING
                    self._init_play()
                    return
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    import sys; sys.exit()
                return

            # ── PLAYING controls ──────────────────────────
            if self.state == State.PLAYING:
                key_map = {
                    pygame.K_w: "up",   pygame.K_UP:    "up",
                    pygame.K_a: "left", pygame.K_LEFT:  "left",
                    pygame.K_d: "right",pygame.K_RIGHT: "right",
                    pygame.K_s: "down", pygame.K_DOWN:  "down",
                }
                if event.key in key_map:
                    self.player.request_move(key_map[event.key])

                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    import sys; sys.exit()

    # ── update ────────────────────────────────────────────
    def update(self, dt: float):
        if self.state == State.START:
            self._blink_timer += dt
            if self._blink_timer >= 0.6:
                self._blink_on = not self._blink_on
                self._blink_timer = 0.0
            return

        if self.state == State.WIN:
            return   # UI animates itself via dt passed in draw

        if self.state == State.DEAD:
            return

        # ── PLAYING ───────────────────────────────────────
        self.player.update(dt)

        # Spawn & update obstacles
        for sp in self.spawners:
            sp.update(dt, self.obstacles)
        for obs in self.obstacles:
            obs.update(dt)
        # Remove off-screen
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        # ── Log riding: push player sideways if standing on a log ──
        self._handle_log_ride(dt)

        # ── Collision detection ───────────────────────────
        p_rect = self.player.get_rect()
        # Shrink player rect slightly for forgiveness
        shrink = 4
        p_rect_small = p_rect.inflate(-shrink * 2, -shrink * 2)

        for obs in self.obstacles:
            # Logs are rideable — never kill the player on collision
            if isinstance(obs, Log):
                continue
            if p_rect_small.colliderect(obs.get_rect()):
                self.state = State.DEAD
                self._finalise_score()
                return

        # ── River drowning ────────────────────────────────
        lane_type = LANE_DEFS[self.player.row][0] if self.player.row < len(LANE_DEFS) else "grass"
        if lane_type == "river":
            if self._on_any_log():
                # Safe — reset grace timer
                self._river_grace = 0.5
            else:
                # Not on a log — count down grace period
                self._river_grace -= dt
                if self._river_grace <= 0 and not self.player._moving:
                    self.state = State.DEAD
                    self._finalise_score()
                    return
        else:
            # Reset grace whenever we leave the river
            self._river_grace = 0.5

        # ── Scoring ───────────────────────────────────────
        if self.player.max_row > self._prev_max:
            self.score += SCORE_PER_ROW * (self.player.max_row - self._prev_max)
            self._prev_max = self.player.max_row

        # Time penalty (gentle drain)
        self.score = max(0, self.score - TIME_PENALTY_PER_SEC * dt)

        # ── Win condition ─────────────────────────────────
        if self.player.row >= ROWS - 1:
            self.score += SCORE_WIN_BONUS
            self._finalise_score()
            self.state = State.WIN

    # ── log-riding helper ─────────────────────────────────
    def _handle_log_ride(self, dt: float):
        """If the player is on a river lane and standing on a log, move with it."""
        lane_type = LANE_DEFS[self.player.row][0] if self.player.row < len(LANE_DEFS) else "grass"
        if lane_type != "river":
            return

        for obs in self.obstacles:
            if not isinstance(obs, Log):
                continue
            if obs.row != self.player.row:
                continue
            # Check if player centre is horizontally within the log
            p_cx = self.player.px + GRID_SIZE // 2
            if obs.x <= p_cx <= obs.x + obs.w:
                # Ride the log
                move = obs.direction * obs.speed * dt
                self.player.px += move
                self.player._target_x += move
                self.player._start_x += move
                # Keep col in sync so the next move starts from the right grid pos
                self.player.col = int((self.player.px + GRID_SIZE // 2) / GRID_SIZE)
                # Push off-screen → die
                if self.player.px < -GRID_SIZE or self.player.px > SCREEN_WIDTH:
                    self.state = State.DEAD
                    self._finalise_score()
                return

    def _on_any_log(self) -> bool:
        lane_type = LANE_DEFS[self.player.row][0] if self.player.row < len(LANE_DEFS) else "grass"
        if lane_type != "river":
            return False
        p_cx = self.player.px + GRID_SIZE // 2
        for obs in self.obstacles:
            if isinstance(obs, Log) and obs.row == self.player.row:
                if obs.x <= p_cx <= obs.x + obs.w:
                    return True
        return False

    def _finalise_score(self):
        int_score = int(self.score)
        if int_score > self.best_score:
            self.best_score = int_score

    # ── draw ──────────────────────────────────────────────
    def draw(self):
        surf = self.screen

        # Background always drawn
        self.background.draw(surf)

        if self.state == State.START:
            self.ui.draw_start(surf, self._blink_on)
            return

        # Obstacles (behind player)
        for obs in self.obstacles:
            obs.draw(surf)

        # Player
        self.player.draw(surf)

        # HUD
        self.ui.draw_hud(surf, int(self.score), self.best_score)

        # Overlays
        if self.state == State.DEAD:
            self.ui.draw_game_over(surf, int(self.score), self.best_score)

        if self.state == State.WIN:
            # Pass a small dt for star animation (approximate)
            self.ui.draw_win(surf, int(self.score), self.best_score, 0.016)