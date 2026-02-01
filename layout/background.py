"""
background.py – Static background (grass, roads, river, decorations)
"""

import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, ROWS, COLS, LANE_DEFS,
    C_BG, C_GRASS_DARK, C_ROAD, C_ROAD_LINE,
    C_SIDEWALK, C_RIVER, C_RIVER_DARK,
    C_TREE, C_TREE_TRUNK, C_FLOWER_RED, C_FLOWER_PINK,
    TREE_CHANCE, FLOWER_CHANCE,
)


class Background:
    def __init__(self):
        # Pre-generate decoration positions so they don't flicker
        random.seed(42)
        self.decorations = []   # list of (col, row, kind, sub)
        for row_idx, (ltype, _, _) in enumerate(LANE_DEFS):
            if ltype == "grass":
                for col in range(COLS + 1):
                    r = random.random()
                    if r < TREE_CHANCE:
                        self.decorations.append((col, row_idx, "tree", 0))
                    elif r < TREE_CHANCE + FLOWER_CHANCE:
                        color = random.choice([C_FLOWER_RED, C_FLOWER_PINK])
                        self.decorations.append((col, row_idx, "flower", color))
        random.seed()   # re-seed normally

        # Pre-render to a surface for speed
        self._surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._render()

    # ── pre-render ────────────────────────────────────────
    def _render(self):
        surf = self._surface

        for row_idx, (ltype, speed, _) in enumerate(LANE_DEFS):
            y = (ROWS - 1 - row_idx) * GRID_SIZE
            self._draw_lane(surf, row_idx, ltype, y)

        # Decorations
        for col, row_idx, kind, sub in self.decorations:
            x = col * GRID_SIZE + GRID_SIZE // 2
            y = (ROWS - 1 - row_idx) * GRID_SIZE + GRID_SIZE // 2
            if kind == "tree":
                self._draw_tree(surf, x, y)
            elif kind == "flower":
                self._draw_flower(surf, x, y, sub)

    def _draw_lane(self, surf, row_idx, ltype, y):
        w = SCREEN_WIDTH
        h = GRID_SIZE

        if ltype == "grass":
            # Alternating shade for visual texture
            base = C_BG if row_idx % 2 == 0 else C_GRASS_DARK
            pygame.draw.rect(surf, base, (0, y, w, h))
            # Subtle stripe
            stripe = tuple(min(c + 8, 255) for c in base)
            for sx in range(0, w, 40):
                pygame.draw.rect(surf, stripe, (sx, y + 2, 20, h - 4))

        elif ltype == "road":
            pygame.draw.rect(surf, C_ROAD, (0, y, w, h))
            # Dashed centre line
            dash_w, gap_w = 30, 20
            cx = 0
            line_y = y + h // 2 - 1
            while cx < w:
                pygame.draw.rect(surf, C_ROAD_LINE, (cx, line_y, dash_w, 2))
                cx += dash_w + gap_w
            # Edge lines
            pygame.draw.line(surf, C_ROAD_LINE, (0, y), (w, y), 2)
            pygame.draw.line(surf, C_ROAD_LINE, (0, y + h - 1), (w, y + h - 1), 2)

        elif ltype == "river":
            pygame.draw.rect(surf, C_RIVER, (0, y, w, h))
            # Wavy highlight strips
            for i in range(3):
                ry = y + 8 + i * 10
                pygame.draw.line(surf, C_RIVER_DARK, (0, ry), (w, ry), 1)
            pygame.draw.line(surf, C_RIVER_DARK, (0, y), (w, y), 2)
            pygame.draw.line(surf, C_RIVER_DARK, (0, y + h - 1), (w, y + h - 1), 2)

        elif ltype == "sidewalk":
            pygame.draw.rect(surf, C_SIDEWALK, (0, y, w, h))
            # Crack pattern
            pygame.draw.line(surf, (160, 150, 130), (50, y + 10), (120, y + h - 10), 1)
            pygame.draw.line(surf, (160, 150, 130), (300, y + 5), (380, y + h - 8), 1)
            pygame.draw.line(surf, (160, 150, 130), (500, y + 12), (560, y + h - 6), 1)

    # ── decoration helpers ────────────────────────────────
    @staticmethod
    def _draw_tree(surf, cx, cy):
        # Trunk
        trunk_w, trunk_h = 8, 14
        pygame.draw.rect(surf, C_TREE_TRUNK,
                         (cx - trunk_w // 2, cy - trunk_h // 2 + 6, trunk_w, trunk_h))
        # Canopy (layered circles)
        pygame.draw.circle(surf, C_TREE, (cx, cy - 8), 14)
        pygame.draw.circle(surf, (28, 85, 8), (cx - 5, cy - 4), 10)
        pygame.draw.circle(surf, (40, 110, 15), (cx + 4, cy - 10), 9)

    @staticmethod
    def _draw_flower(surf, cx, cy, color):
        # Stem
        pygame.draw.line(surf, (60, 100, 20), (cx, cy + 2), (cx, cy + 12), 2)
        # Petals
        for dx, dy in [(-3, -4), (3, -4), (0, -7), (-5, -1), (5, -1)]:
            pygame.draw.circle(surf, color, (cx + dx, cy + dy), 3)
        # Centre
        pygame.draw.circle(surf, (255, 230, 50), (cx, cy - 3), 2)

    # ── public draw ───────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        surface.blit(self._surface, (0, 0))