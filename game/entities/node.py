import pygame
from game.settings import NODE_RADIUS, ENTROPY_MAX, SOURCE_COLOR, GROUND_COLOR


class Node:
    def __init__(self, x, y, entropy_rate=1.0, node_type="regular"):
        self.x = x
        self.y = y
        self.entropy = 0.0
        self.entropy_rate = entropy_rate
        self.node_type = node_type  # "regular", "source", "ground"
        self.wires = []
        self.components = []
        self.peak_entropy = 0.0

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def is_source(self):
        return self.node_type == "source"

    @property
    def is_ground(self):
        return self.node_type == "ground"

    @property
    def entropy_ratio(self):
        return min(1.0, self.entropy / ENTROPY_MAX)

    @property
    def overloaded(self):
        # Source and ground nodes can't overload — they're infrastructure
        if self.is_source or self.is_ground:
            return False
        return self.entropy >= ENTROPY_MAX

    def _entropy_color(self):
        r = self.entropy_ratio
        if self.is_source:
            # amber → orange → red
            red = int(min(255, SOURCE_COLOR[0] + 35 * r))
            green = int(max(40, SOURCE_COLOR[1] * (1 - r * 0.7)))
            blue = int(max(20, SOURCE_COLOR[2] * (1 - r)))
            return (red, green, blue)
        elif self.is_ground:
            # blue → purple → red
            red = int(min(255, GROUND_COLOR[0] + 195 * r))
            green = int(max(40, GROUND_COLOR[1] * (1 - r * 0.6)))
            blue = int(max(40, GROUND_COLOR[2] * (1 - r * 0.5)))
            return (red, green, blue)
        else:
            # green → yellow → red
            red = int(min(255, 80 + 175 * r))
            green = int(max(50, 220 * (1 - r)))
            blue = int(max(30, 80 * (1 - r)))
            return (red, green, blue)

    def draw(self, surf):
        r = self.entropy_ratio
        color = self._entropy_color()

        # Outer glow when hot
        if r > 0.6:
            glow_r = NODE_RADIUS + int(6 * r)
            glow_alpha = int(60 * r)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_r, glow_r), glow_r)
            surf.blit(glow_surf, (self.x - glow_r, self.y - glow_r))

        if self.is_source:
            self._draw_source(surf, color)
        elif self.is_ground:
            self._draw_ground(surf, color)
        else:
            self._draw_regular(surf, color)

        # Entropy bar (shared)
        self._draw_entropy_bar(surf, color, r)

    def _draw_regular(self, surf, color):
        pygame.draw.circle(surf, color, (self.x, self.y), NODE_RADIUS)
        pygame.draw.circle(surf, (255, 255, 255), (self.x, self.y), NODE_RADIUS, 2)

    def _draw_source(self, surf, color):
        # Rounded square
        size = NODE_RADIUS + 2
        rect = pygame.Rect(self.x - size, self.y - size, size * 2, size * 2)
        pygame.draw.rect(surf, color, rect, border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=5)
        # "+" symbol
        cx, cy = self.x, self.y
        t = 2
        pygame.draw.line(surf, (255, 255, 255), (cx - 6, cy), (cx + 6, cy), t)
        pygame.draw.line(surf, (255, 255, 255), (cx, cy - 6), (cx, cy + 6), t)

    def _draw_ground(self, surf, color):
        # Circle with ground symbol beneath
        pygame.draw.circle(surf, color, (self.x, self.y), NODE_RADIUS)
        pygame.draw.circle(surf, (255, 255, 255), (self.x, self.y), NODE_RADIUS, 2)
        # Three horizontal lines below (ground symbol)
        by = self.y + NODE_RADIUS + 3
        for i, w in enumerate([10, 7, 4]):
            pygame.draw.line(surf, GROUND_COLOR,
                             (self.x - w, by + i * 4),
                             (self.x + w, by + i * 4), 2)

    def _draw_entropy_bar(self, surf, color, r):
        bar_w = 36
        bar_h = 5
        bx = self.x - bar_w // 2
        by = self.y - NODE_RADIUS - 12
        if self.is_source:
            by = self.y - (NODE_RADIUS + 2) - 12
        pygame.draw.rect(surf, (50, 50, 60), (bx, by, bar_w, bar_h), border_radius=2)
        fill = int(bar_w * r)
        if fill > 0:
            pygame.draw.rect(surf, color, (bx, by, fill, bar_h), border_radius=2)

    def draw_highlight(self, surf):
        if self.is_source:
            size = NODE_RADIUS + 8
            rect = pygame.Rect(self.x - size, self.y - size, size * 2, size * 2)
            pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=7)
        else:
            pygame.draw.circle(surf, (255, 255, 255), (self.x, self.y), NODE_RADIUS + 6, 2)
