import pygame
import sys
import math

from game.settings import (
    WIDTH, HEIGHT, FPS, TACTICAL_DURATION,
    ACCENT, DANGER, SUCCESS, TEXT_COLOR, MUTED,
)
from game.states import GameState
from game.level import Level
from game.levels.definitions import LEVELS
from game.inventory import Inventory
from game.entities.component import COMPONENT_TYPES, Transistor
from game.entities.wire import Wire
from game import simulation
from game.ui.hud import HUD
from game.ui.palette import Palette
from game.ui.drag import DragManager


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Electropy — Entropic Circuits")
        self.clock = pygame.time.Clock()

        self.hud = HUD()
        self.palette = Palette()
        self.drag = DragManager()
        self.inventory = Inventory()

        self.state = GameState.MENU
        self.levels_unlocked = 1
        self.current_level_idx = 0
        self.level = None
        self.placed_components = []
        self.overlay_buttons = {}
        self.earned = 0

        # Tactical mode
        self.tactical_active = False
        self.tactical_remaining = 0.0

        # Give starter for level 1
        self.inventory.give_starter(LEVELS[0].get("starter", {}))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.state == GameState.MENU:
                self._update_menu(events)
            elif self.state == GameState.PLAYING:
                self._update_playing(events, dt)
            elif self.state == GameState.LEVEL_COMPLETE:
                self._update_overlay(events)
            elif self.state == GameState.GAME_OVER:
                self._update_overlay(events)

            pygame.display.flip()

    def _start_level(self, idx):
        self.current_level_idx = idx
        defn = LEVELS[idx]
        self.level = Level(defn)
        self.placed_components = []
        self.drag.cancel()
        self.tactical_active = False
        self.tactical_remaining = 0.0
        self.inventory.give_starter(defn.get("starter", {}))
        self.state = GameState.PLAYING

    # ========== MENU ==========
    def _update_menu(self, events):
        self.screen.fill((18, 18, 28))
        btn_y = self.hud.draw_menu(self.screen, self.levels_unlocked, self.inventory)

        level_buttons = {}
        font = self.hud.font_large
        for i, defn in enumerate(LEVELS):
            unlocked = i < self.levels_unlocked
            color = ACCENT if unlocked else MUTED
            label = f"{i+1}. {defn['name']}"
            if not unlocked:
                label += " [LOCKED]"
            text = font.render(label, True, color)
            btn_rect = pygame.Rect(WIDTH // 2 - 160, btn_y, 320, 40)
            if unlocked:
                pygame.draw.rect(self.screen, (40, 40, 60), btn_rect, border_radius=6)
                pygame.draw.rect(self.screen, color, btn_rect, 2, border_radius=6)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                    btn_rect.centery - text.get_height() // 2))
            level_buttons[i] = (btn_rect, unlocked)
            btn_y += 52

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for idx, (rect, unlocked) in level_buttons.items():
                    if unlocked and rect.collidepoint(mx, my):
                        self._start_level(idx)
                        return

    # ========== PLAYING ==========
    def _update_playing(self, events, dt):
        level = self.level

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # --- RIGHT CLICK: cancel drag or remove component/wire ---
                if event.button == 3:
                    if self.drag.active:
                        self.drag.cancel()
                        continue
                    # Try removing a placed component
                    if self._try_remove_component(mx, my):
                        continue
                    # Try removing a wire
                    if self._try_remove_wire(mx, my):
                        continue

                # --- LEFT CLICK ---
                if event.button == 1:
                    # Wire placement mode: two-click flow
                    if self.drag.wire_mode:
                        if self.drag.wire_start_node is None:
                            # First click: select start node
                            node = self._nearest_node(mx, my)
                            if node:
                                self.drag.wire_start_node = node
                        else:
                            # Second click: select end node and create wire
                            node = self._nearest_node(mx, my)
                            if node and node is not self.drag.wire_start_node:
                                # Check no duplicate wire
                                duplicate = any(
                                    w.connects(self.drag.wire_start_node, node)
                                    for w in level.wires
                                )
                                if not duplicate:
                                    wire = Wire(self.drag.wire_start_node, node)
                                    level.wires.append(wire)
                                    self.inventory.spend("Wire")
                                    level.components_used += 1
                                self.drag.cancel_wire()
                            elif node is self.drag.wire_start_node:
                                # Clicked same node, cancel
                                self.drag.cancel_wire()
                        continue

                    # Transistor trigger (only when not dragging)
                    if not self.drag.active:
                        for comp in self.placed_components:
                            if isinstance(comp, Transistor) and comp.attached_node:
                                cx, cy = comp.pos
                                if math.hypot(mx - cx, my - cy) < 20:
                                    comp.trigger()
                                    break

                    # Palette click
                    if my > self.palette.top:
                        name = self.palette.hit_test(mx, my)
                        if name and self.inventory.has(name):
                            if name == "Wire":
                                self.drag.start_wire()
                            elif name == "Tactical":
                                # Don't "drag" tactical — activate immediately
                                if not self.tactical_active:
                                    self.inventory.spend("Tactical")
                                    self.tactical_active = True
                                    self.tactical_remaining = TACTICAL_DURATION
                            else:
                                cls = COMPONENT_TYPES[name]
                                self.drag.start(cls)
                                self.drag._drag_name = name
                        continue

                    # Place component if dragging
                    if self.drag.active:
                        name = getattr(self.drag, '_drag_name', self.drag.dragging.name)
                        if self.drag.place(level, self.placed_components):
                            self.inventory.spend(name)
                            level.components_used += 1
                        continue

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                self.drag.update(mx, my, level)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.drag.active or self.drag.wire_mode:
                        self.drag.cancel()
                        self.drag.cancel_wire()
                elif event.key == pygame.K_SPACE:
                    if not self.tactical_active and self.inventory.has("Tactical"):
                        self.inventory.spend("Tactical")
                        self.tactical_active = True
                        self.tactical_remaining = TACTICAL_DURATION

        # Simulation (skip during tactical mode)
        if self.tactical_active:
            self.tactical_remaining -= dt
            if self.tactical_remaining <= 0:
                self.tactical_active = False
                self.tactical_remaining = 0.0
        else:
            simulation.tick(level.nodes, level.wires, dt)
            level.tick(dt)

        # ===== DRAW =====
        self.screen.fill((18, 18, 28))

        for wire in level.wires:
            wire.draw(self.screen)
        for node in level.nodes:
            node.draw(self.screen)
        for comp in self.placed_components:
            comp.draw(self.screen, self.hud.font)

        self.palette.draw(self.screen, self.inventory, self.hud.font)
        self.hud.draw_playing(self.screen, level, self.inventory,
                              self.tactical_active, self.tactical_remaining)
        self.drag.draw(self.screen, self.hud.font, level)

        # Tactical mode tint
        if self.tactical_active:
            tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            tint.fill((40, 80, 140, 30))
            self.screen.blit(tint, (0, 0))

        # Check win/loss (win takes priority — if timer hits 0 same frame as overload, you win)
        if level.won:
            self.earned = level.calculate_output()
            self.state = GameState.LEVEL_COMPLETE
        elif level.lost:
            self.state = GameState.GAME_OVER
            self.earned = 0

    # ========== COMPONENT/WIRE REMOVAL ==========
    def _try_remove_component(self, mx, my):
        for comp in list(self.placed_components):
            cx, cy = comp.pos
            if math.hypot(mx - cx, my - cy) < 22:
                # Remove from node or wire
                if comp.attached_node:
                    comp.attached_node.components.remove(comp)
                    comp.attached_node = None
                if comp.attached_wire:
                    comp.attached_wire.diode = None
                    comp.attached_wire = None
                self.placed_components.remove(comp)
                self.inventory.earn(comp.name, 1)
                level = self.level
                if level:
                    level.components_used = max(0, level.components_used - 1)
                return True
        return False

    def _try_remove_wire(self, mx, my):
        level = self.level
        if not level:
            return False
        for wire in list(level.wires):
            if wire.hit_test(mx, my):
                # Grab diode reference before destroy clears it
                attached_diode = wire.diode
                diode_name = wire.destroy()
                level.wires.remove(wire)
                self.inventory.earn("Wire", 1)
                # Refund diode if one was attached
                if diode_name and attached_diode:
                    if attached_diode in self.placed_components:
                        self.placed_components.remove(attached_diode)
                    self.inventory.earn(diode_name, 1)
                    self.inventory.earn(diode_name, 1)
                return True
        return False

    def _nearest_node(self, mx, my):
        from game.settings import NODE_SNAP_DIST
        best = None
        best_dist = NODE_SNAP_DIST
        for node in self.level.nodes:
            d = math.hypot(mx - node.x, my - node.y)
            if d < best_dist:
                best_dist = d
                best = node
        return best

    # ========== OVERLAYS ==========
    def _update_overlay(self, events):
        if self.level:
            self.screen.fill((18, 18, 28))
            for wire in self.level.wires:
                wire.draw(self.screen)
            for node in self.level.nodes:
                node.draw(self.screen)
            for comp in self.placed_components:
                comp.draw(self.screen, self.hud.font)

        if self.state == GameState.LEVEL_COMPLETE:
            survived = self.level.survive_time
            self.overlay_buttons = self.hud.draw_overlay(
                self.screen,
                "LEVEL COMPLETE",
                f"Survived {survived:.0f}s",
                SUCCESS,
                options=["Next Level", "Replay", "Menu"],
            )
            self.hud.draw_score(self.screen, self.level, self.earned)
        elif self.state == GameState.GAME_OVER:
            elapsed = self.level.survive_time - self.level.time_remaining
            self.overlay_buttons = self.hud.draw_overlay(
                self.screen,
                "CIRCUIT OVERLOAD",
                f"Survived {elapsed:.1f}s / {self.level.survive_time:.0f}s",
                DANGER,
                options=["Retry", "Menu"],
            )

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for label, rect in self.overlay_buttons.items():
                    if rect.collidepoint(mx, my):
                        self._handle_overlay_click(label)
                        return

    def _handle_overlay_click(self, label):
        if label == "Next Level":
            self._award_components()
            next_idx = self.current_level_idx + 1
            if next_idx < len(LEVELS):
                self.levels_unlocked = max(self.levels_unlocked, next_idx + 1)
                self._start_level(next_idx)
            else:
                self.state = GameState.MENU
        elif label == "Replay":
            self._start_level(self.current_level_idx)
        elif label == "Retry":
            self._start_level(self.current_level_idx)
        elif label == "Menu":
            if self.state == GameState.LEVEL_COMPLETE:
                self._award_components()
            self.state = GameState.MENU

    def _award_components(self):
        if self.earned <= 0:
            return
        mfg = self.level.manufactures
        if isinstance(mfg, dict):
            # Dict-based manufacturing: {"Capacitor": 3, "Wire": 2}
            for name, base in mfg.items():
                # Scale by performance ratio
                ratio = self.earned / max(1, self.level.max_output)
                amount = max(1, int(base * ratio))
                self.inventory.earn(name, amount)
        elif mfg == "all":
            for name in ["Resistor", "Capacitor", "Diode", "Transistor", "Wire", "Tactical"]:
                self.inventory.earn(name, self.earned)
        else:
            self.inventory.earn(mfg, self.earned)
