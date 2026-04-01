import pygame
import math
from game.settings import WIRE_COLOR, WIRE_HOT_COLOR, WIRE_CLICK_DIST


class Wire:
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
        self.diode = None  # if set, a Diode component restricting flow direction
        # Register on both nodes
        node_a.wires.append(self)
        node_b.wires.append(self)

    @property
    def midpoint(self):
        return (
            (self.node_a.x + self.node_b.x) // 2,
            (self.node_a.y + self.node_b.y) // 2,
        )

    def other(self, node):
        return self.node_b if node is self.node_a else self.node_a

    def dist_to_point(self, px, py):
        ax, ay = self.node_a.x, self.node_a.y
        bx, by = self.node_b.x, self.node_b.y
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / length_sq))
        proj_x = ax + t * dx
        proj_y = ay + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def hit_test(self, px, py):
        return self.dist_to_point(px, py) < WIRE_CLICK_DIST

    def destroy(self):
        if self in self.node_a.wires:
            self.node_a.wires.remove(self)
        if self in self.node_b.wires:
            self.node_b.wires.remove(self)
        # Return diode name if one was attached (for inventory refund)
        diode_name = None
        if self.diode:
            diode_name = self.diode.name
            self.diode = None
        return diode_name

    def connects(self, node_a, node_b):
        return (self.node_a is node_a and self.node_b is node_b) or \
               (self.node_a is node_b and self.node_b is node_a)

    def draw(self, surf):
        # color based on max entropy of connected nodes
        max_e = max(self.node_a.entropy_ratio, self.node_b.entropy_ratio)
        r = int(WIRE_COLOR[0] + (WIRE_HOT_COLOR[0] - WIRE_COLOR[0]) * max_e)
        g = int(WIRE_COLOR[1] + (WIRE_HOT_COLOR[1] - WIRE_COLOR[1]) * max_e)
        b = int(WIRE_COLOR[2] + (WIRE_HOT_COLOR[2] - WIRE_COLOR[2]) * max_e)
        thickness = 3 + int(3 * max_e)
        pygame.draw.line(surf, (r, g, b),
                         (self.node_a.x, self.node_a.y),
                         (self.node_b.x, self.node_b.y), thickness)

    def draw_highlight(self, surf):
        pygame.draw.line(surf, (255, 255, 255),
                         (self.node_a.x, self.node_a.y),
                         (self.node_b.x, self.node_b.y), 2)
