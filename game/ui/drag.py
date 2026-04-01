import pygame
import math
from game.settings import NODE_SNAP_DIST, WIRE_CLICK_DIST, COMPONENT_COLORS
from game.entities.component import Diode


class DragManager:
    def __init__(self):
        self.dragging = None  # Component instance being dragged
        self.drag_pos = (0, 0)
        self.snap_node = None
        self.snap_wire = None
        self._drag_name = None

        # Wire placement mode
        self.wire_mode = False
        self.wire_start_node = None

    @property
    def active(self):
        return self.dragging is not None

    def start(self, component_cls):
        self.dragging = component_cls()
        self.snap_node = None
        self.snap_wire = None

    def start_wire(self):
        self.wire_mode = True
        self.wire_start_node = None

    def cancel(self):
        self.dragging = None
        self.snap_node = None
        self.snap_wire = None
        self._drag_name = None

    def cancel_wire(self):
        self.wire_mode = False
        self.wire_start_node = None

    def update(self, mx, my, level):
        self.drag_pos = (mx, my)
        self.snap_node = None
        self.snap_wire = None

        # Wire mode: always snap to nearest node
        if self.wire_mode:
            best_node = None
            best_dist = NODE_SNAP_DIST
            for node in level.nodes:
                if node is self.wire_start_node:
                    continue
                d = math.hypot(mx - node.x, my - node.y)
                if d < best_dist:
                    best_dist = d
                    best_node = node
            self.snap_node = best_node
            return

        if not self.dragging:
            return

        if self.dragging.attaches_to == "wire":
            best_wire = None
            best_dist = WIRE_CLICK_DIST + 10
            for wire in level.wires:
                d = wire.dist_to_point(mx, my)
                if d < best_dist and wire.diode is None:
                    best_dist = d
                    best_wire = wire
            self.snap_wire = best_wire
        else:
            best_node = None
            best_dist = NODE_SNAP_DIST
            for node in level.nodes:
                d = math.hypot(mx - node.x, my - node.y)
                if d < best_dist:
                    best_dist = d
                    best_node = node
            self.snap_node = best_node

    def place(self, level, placed_components):
        if not self.dragging:
            return False

        comp = self.dragging

        if comp.attaches_to == "wire" and self.snap_wire:
            wire = self.snap_wire
            comp.attached_wire = wire
            wire.diode = comp
            placed_components.append(comp)
            self.dragging = None
            self.snap_wire = None
            return True
        elif comp.attaches_to == "node" and self.snap_node:
            node = self.snap_node
            for existing in node.components:
                if existing.name == comp.name:
                    return False
            comp.attached_node = node
            node.components.append(comp)
            placed_components.append(comp)
            self.dragging = None
            self.snap_node = None
            return True

        return False

    def draw(self, surf, font, level):
        mx, my = self.drag_pos

        # Wire placement preview
        if self.wire_mode:
            wire_color = COMPONENT_COLORS.get("Wire", (180, 180, 200))
            if self.wire_start_node:
                # Draw line from start node to cursor (or snap node)
                start = (self.wire_start_node.x, self.wire_start_node.y)
                self.wire_start_node.draw_highlight(surf)
                if self.snap_node:
                    end = (self.snap_node.x, self.snap_node.y)
                    self.snap_node.draw_highlight(surf)
                else:
                    end = (mx, my)
                pygame.draw.line(surf, (*wire_color, 180), start, end, 3)
            else:
                # Waiting for first click — highlight nearest node
                if self.snap_node:
                    self.snap_node.draw_highlight(surf)
                # Draw wire icon at cursor
                label = font.render("W", True, wire_color)
                surf.blit(label, (mx - label.get_width() // 2, my - label.get_height() // 2 - 16))
            return

        if not self.dragging:
            return

        # Draw snap highlight
        if self.snap_node:
            self.snap_node.draw_highlight(surf)
        if self.snap_wire:
            self.snap_wire.draw_highlight(surf)

        # Draw ghost component at cursor
        comp = self.dragging
        ghost_surf = pygame.Surface((40, 28), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, 40, 28)
        pygame.draw.rect(ghost_surf, (*comp.color, 150), rect, border_radius=5)
        label = font.render(comp.name[0], True, (255, 255, 255))
        ghost_surf.blit(label, (20 - label.get_width() // 2, 14 - label.get_height() // 2))
        surf.blit(ghost_surf, (mx - 20, my - 14))
