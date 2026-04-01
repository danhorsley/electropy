import pygame
from game.settings import BG_COLOR


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw(self, level, placed_components, palette, hud, drag_manager):
        self.screen.fill(BG_COLOR)

        # 1. Wires
        for wire in level.wires:
            wire.draw(self.screen)

        # 2. Nodes
        for node in level.nodes:
            node.draw(self.screen)

        # 3. Placed components
        font = hud.font
        for comp in placed_components:
            comp.draw(self.screen, font)

        # 4. Palette (solid bg + component icons)
        palette.draw(self.screen)

        # 5. HUD
        hud.draw(self.screen)

        # 6. Drag ghost + snap highlight (on top of everything)
        drag_manager.draw(self.screen, font, level)

        pygame.display.flip()
