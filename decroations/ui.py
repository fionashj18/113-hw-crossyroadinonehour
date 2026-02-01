"""
ui.py – Heads-up display, menus, overlays
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, ROWS,
    C_TEXT, C_TEXT_SHADOW, C_OVERLAY, C_STAR, C_WIN_BG,
    C_CHICKEN, C_CHICKEN_BEAK,
)


def _shadow_text(surface, font, text, x, y, color=C_TEXT, shadow=C_TEXT_SHADOW):
    """Draw text with a drop-shadow for readability."""
    s = font.render(text, True, shadow)
    surface.blit(s, (x + 2, y + 2))
    s = font.render(text, True, color)
    surface.blit(s, (x, y))


class UI:
    def __init__(self):
        self.font_large  = pygame.font.SysFont("arial", 56, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 34, bold=True)
        self.font_small  = pygame.font.SysFont("arial, helvetica", 22)
        self.font_tiny   = pygame.font.SysFont("arial", 18)

        # Star animation state
        self._star_time = 0.0

    # ── HUD (in-game) ─────────────────────────────────────
    def draw_hud(self, surface: pygame.Surface, score: int, best: int):
        # Score box – top left
        box_w, box_h = 150, 44
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 140))
        surface.blit(box_surf, (8, 8))
        pygame.draw.rect(surface, (255, 255, 255), (8, 8, box_w, box_h), 2, border_radius=6)
        _shadow_text(surface, self.font_small, f"Score: {score}", 18, 14)

        # Best box – top right
        bx = SCREEN_WIDTH - box_w - 8
        box_surf2 = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf2.fill((0, 0, 0, 140))
        surface.blit(box_surf2, (bx, 8))
        pygame.draw.rect(surface, (255, 215, 0), (bx, 8, box_w, box_h), 2, border_radius=6)
        _shadow_text(surface, self.font_small, f"Best: {best}", bx + 10, 14, color=(255, 215, 0))

    # ── Start screen ──────────────────────────────────────
    def draw_start(self, surface: pygame.Surface, blink_on: bool):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        cy = SCREEN_HEIGHT // 2

        # Title
        _shadow_text(surface, self.font_large, "CROSSY ROAD",
                     0, cy - 160,
                     color=(255, 220, 50), shadow=(80, 60, 0))
        # Centre it
        title_w = self.font_large.size("CROSSY ROAD")[0]
        # Re-draw centred
        surface.fill((0, 0, 0, 0))  # won't work on non-alpha; just blit again
        # Simpler: just compute x
        tx = (SCREEN_WIDTH - title_w) // 2
        _shadow_text(surface, self.font_large, "CROSSY ROAD",
                     tx, cy - 160,
                     color=(255, 220, 50), shadow=(80, 60, 0))

        # Little chicken icon
        self._draw_mini_chicken(surface, SCREEN_WIDTH // 2, cy - 60)

        # Instructions
        _shadow_text(surface, self.font_small,
                     "Help the chicken cross the road!",
                     0, cy + 10)
        inst_w = self.font_small.size("Help the chicken cross the road!")[0]
        # re-centre
        _shadow_text(surface, self.font_small,
                     "Help the chicken cross the road!",
                     (SCREEN_WIDTH - inst_w) // 2, cy + 10)

        controls = "W/↑ Up   A/← Left   D/→ Right   S/↓ Down"
        cw = self.font_tiny.size(controls)[0]
        _shadow_text(surface, self.font_tiny, controls,
                     (SCREEN_WIDTH - cw) // 2, cy + 48)

        # Blinking "Press any key"
        if blink_on:
            msg = "— Press any key to start —"
            mw = self.font_medium.size(msg)[0]
            _shadow_text(surface, self.font_medium, msg,
                         (SCREEN_WIDTH - mw) // 2, cy + 100,
                         color=(255, 255, 255))

    # ── Game Over ─────────────────────────────────────────
    def draw_game_over(self, surface: pygame.Surface, score: int, best: int):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        cy = SCREEN_HEIGHT // 2

        # "GAME OVER"
        txt = "GAME OVER"
        tw = self.font_large.size(txt)[0]
        _shadow_text(surface, self.font_large, txt,
                     (SCREEN_WIDTH - tw) // 2, cy - 100,
                     color=(220, 60, 60), shadow=(80, 0, 0))

        # Score
        s_txt = f"Score: {score}"
        sw = self.font_medium.size(s_txt)[0]
        _shadow_text(surface, self.font_medium, s_txt,
                     (SCREEN_WIDTH - sw) // 2, cy - 20)

        # Best
        b_txt = f"Best: {best}"
        bw = self.font_medium.size(b_txt)[0]
        _shadow_text(surface, self.font_medium, b_txt,
                     (SCREEN_WIDTH - bw) // 2, cy + 22,
                     color=(255, 215, 0))

        # Restart hint
        r_txt = "Press R to Restart  |  Q to Quit"
        rw = self.font_small.size(r_txt)[0]
        _shadow_text(surface, self.font_small, r_txt,
                     (SCREEN_WIDTH - rw) // 2, cy + 80)

    # ── Win screen ────────────────────────────────────────
    def draw_win(self, surface: pygame.Surface, score: int, best: int, dt: float):
        self._star_time += dt

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 60, 190))
        surface.blit(overlay, (0, 0))

        cy = SCREEN_HEIGHT // 2

        # Animated stars
        for i in range(12):
            angle = (self._star_time * 1.5 + i * (2 * math.pi / 12))
            sx = SCREEN_WIDTH // 2 + int(180 * math.cos(angle))
            sy = cy - 80 + int(40 * math.sin(angle * 2 + i))
            size = 6 + int(3 * math.sin(self._star_time * 3 + i))
            alpha = 180 + int(75 * math.sin(self._star_time * 2 + i * 0.7))
            star_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (*C_STAR, alpha), (size, size), size)
            surface.blit(star_surf, (sx - size, sy - size))

        # "YOU WIN!"
        txt = "YOU WIN!"
        tw = self.font_large.size(txt)[0]
        _shadow_text(surface, self.font_large, txt,
                     (SCREEN_WIDTH - tw) // 2, cy - 140,
                     color=(80, 255, 140), shadow=(0, 60, 30))

        # Score
        s_txt = f"Score: {score}"
        sw = self.font_medium.size(s_txt)[0]
        _shadow_text(surface, self.font_medium, s_txt,
                     (SCREEN_WIDTH - sw) // 2, cy - 30)

        b_txt = f"Best: {best}"
        bw = self.font_medium.size(b_txt)[0]
        _shadow_text(surface, self.font_medium, b_txt,
                     (SCREEN_WIDTH - bw) // 2, cy + 16,
                     color=(255, 215, 0))

        # Chicken celebration
        self._draw_mini_chicken(surface, SCREEN_WIDTH // 2, cy + 70)

        r_txt = "Press R to Play Again  |  Q to Quit"
        rw = self.font_small.size(r_txt)[0]
        _shadow_text(surface, self.font_small, r_txt,
                     (SCREEN_WIDTH - rw) // 2, cy + 110)

    # ── mini chicken (for menus) ──────────────────────────
    @staticmethod
    def _draw_mini_chicken(surface, cx, cy):
        s = 36
        # Body
        pygame.draw.ellipse(surface, C_CHICKEN,
                            (cx - s // 2, cy - s // 2 + 2, s, s - 4))
        pygame.draw.ellipse(surface, (200, 180, 140),
                            (cx - s // 2, cy - s // 2 + 2, s, s - 4), 2)
        # Head
        hr = s // 4
        hx, hy = cx, cy - s // 2 - hr + 6
        pygame.draw.circle(surface, C_CHICKEN, (hx, hy), hr)
        # Eye
        pygame.draw.circle(surface, (20, 20, 20), (hx + 2, hy - 2), 3)
        pygame.draw.circle(surface, (255, 255, 255), (hx + 3, hy - 3), 1)
        # Beak
        pygame.draw.polygon(surface, C_CHICKEN_BEAK,
                            [(hx - 2, hy - hr - 1), (hx + 2, hy - hr - 1), (hx, hy - hr - 5)])
        # Legs
        leg_y = cy + s // 2 - 2
        pygame.draw.line(surface, (200, 160, 60), (cx - 4, leg_y), (cx - 4, leg_y + 5), 2)
        pygame.draw.line(surface, (200, 160, 60), (cx + 4, leg_y), (cx + 4, leg_y + 5), 2)