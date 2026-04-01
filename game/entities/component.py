import pygame
import math
from game.settings import (
    COMPONENT_COLORS, TRANSISTOR_COOLDOWN,
    CAPACITOR_THRESHOLD, CAPACITOR_MAX_CHARGE,
    CAPACITOR_ABSORB_RATE, CAPACITOR_DISCHARGE_RATE,
)


class Component:
    name = "Component"
    attaches_to = "node"  # "node" or "wire"

    def __init__(self):
        self.attached_node = None
        self.attached_wire = None

    @property
    def color(self):
        return COMPONENT_COLORS.get(self.name, (150, 150, 150))

    @property
    def pos(self):
        if self.attached_node:
            return (self.attached_node.x, self.attached_node.y + 22)
        if self.attached_wire:
            return self.attached_wire.midpoint
        return (0, 0)

    def apply(self, dt):
        pass

    def draw(self, surf, font):
        x, y = self.pos
        rect = pygame.Rect(x - 16, y - 10, 32, 20)
        pygame.draw.rect(surf, self.color, rect, border_radius=5)
        label = font.render(self.name[0], True, (255, 255, 255))
        surf.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))

    def draw_cooldown(self, surf):
        pass


class Resistor(Component):
    name = "Resistor"
    reduction = 0.4  # multiplier on entropy growth (lower = stronger)

    def apply(self, dt):
        pass  # handled in simulation — reduces growth rate


class Capacitor(Component):
    name = "Capacitor"

    def __init__(self):
        super().__init__()
        self.charge = 0.0

    @property
    def full(self):
        return self.charge >= CAPACITOR_MAX_CHARGE

    def apply(self, dt):
        node = self.attached_node
        if not node:
            return
        if not self.full and node.entropy > CAPACITOR_THRESHOLD:
            absorb = min(CAPACITOR_ABSORB_RATE * dt, node.entropy - CAPACITOR_THRESHOLD)
            absorb = min(absorb, CAPACITOR_MAX_CHARGE - self.charge)
            node.entropy -= absorb
            self.charge += absorb
        elif self.full:
            discharge = CAPACITOR_DISCHARGE_RATE * dt
            discharge = min(discharge, self.charge)
            node.entropy += discharge
            self.charge -= discharge

    def draw(self, surf, font):
        x, y = self.pos
        rect = pygame.Rect(x - 16, y - 10, 32, 20)
        pygame.draw.rect(surf, self.color, rect, border_radius=5)
        # charge indicator
        charge_ratio = self.charge / CAPACITOR_MAX_CHARGE
        fill_w = int(28 * charge_ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(x - 14, y + 6, fill_w, 3)
            pygame.draw.rect(surf, (200, 200, 255), fill_rect, border_radius=1)
        label = font.render("C", True, (255, 255, 255))
        surf.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))


class Diode(Component):
    name = "Diode"
    attaches_to = "wire"

    def __init__(self):
        super().__init__()
        # flow_direction: entropy can only flow from node_a → node_b on the wire
        # the player can click to flip direction
        self.flipped = False

    @property
    def allowed_from(self):
        if not self.attached_wire:
            return None
        return self.attached_wire.node_b if self.flipped else self.attached_wire.node_a

    @property
    def allowed_to(self):
        if not self.attached_wire:
            return None
        return self.attached_wire.node_a if self.flipped else self.attached_wire.node_b

    def apply(self, dt):
        pass  # handled in simulation — blocks propagation in one direction

    def draw(self, surf, font):
        if not self.attached_wire:
            return
        mx, my = self.attached_wire.midpoint
        # triangle arrow showing flow direction
        w = self.attached_wire
        dx = w.node_b.x - w.node_a.x
        dy = w.node_b.y - w.node_a.y
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        if self.flipped:
            ux, uy = -ux, -uy
        # perpendicular
        px, py = -uy, ux
        size = 10
        tip = (mx + ux * size, my + uy * size)
        left = (mx - ux * 4 + px * 7, my - uy * 4 + py * 7)
        right = (mx - ux * 4 - px * 7, my - uy * 4 - py * 7)
        pygame.draw.polygon(surf, self.color, [tip, left, right])
        # bar at base
        bar_start = (mx - ux * 5 + px * 8, my - uy * 5 + py * 8)
        bar_end = (mx - ux * 5 - px * 8, my - uy * 5 - py * 8)
        pygame.draw.line(surf, self.color, bar_start, bar_end, 3)


class Transistor(Component):
    name = "Transistor"

    def __init__(self):
        super().__init__()
        self.cooldown = 0.0
        self.ready = True

    def apply(self, dt):
        if self.cooldown > 0:
            self.cooldown = max(0, self.cooldown - dt)
            self.ready = self.cooldown <= 0

    def trigger(self):
        node = self.attached_node
        if not node or not self.ready:
            return False
        if not node.wires:
            return False
        # dump: spread this node's entropy evenly to connected nodes
        connected = [w.other(node) for w in node.wires]
        if not connected:
            return False
        dump_per = node.entropy * 0.6 / len(connected)
        node.entropy *= 0.4
        for other in connected:
            other.entropy = min(100.0, other.entropy + dump_per)
        self.cooldown = TRANSISTOR_COOLDOWN
        self.ready = False
        return True

    def draw(self, surf, font):
        x, y = self.pos
        rect = pygame.Rect(x - 16, y - 10, 32, 20)
        color = self.color if self.ready else (100, 100, 60)
        pygame.draw.rect(surf, color, rect, border_radius=5)
        label = font.render("T", True, (255, 255, 255))
        surf.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))
        # cooldown arc
        if not self.ready:
            ratio = self.cooldown / TRANSISTOR_COOLDOWN
            arc_rect = pygame.Rect(x - 18, y - 12, 36, 24)
            end_angle = math.pi * 2 * ratio
            if end_angle > 0.01:
                pygame.draw.arc(surf, (200, 200, 50), arc_rect,
                                -math.pi / 2, -math.pi / 2 + end_angle, 2)

    def draw_cooldown(self, surf):
        pass  # handled in draw


COMPONENT_TYPES = {
    "Resistor": Resistor,
    "Capacitor": Capacitor,
    "Diode": Diode,
    "Transistor": Transistor,
}
