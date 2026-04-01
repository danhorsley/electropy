import pygame
from game.settings import (
    WIDTH, HEIGHT, PALETTE_HEIGHT, PALETTE_BG,
    COMPONENT_COLORS, MUTED, TEXT_COLOR,
)


PALETTE_ITEMS = ["Resistor", "Capacitor", "Diode", "Transistor", "Wire", "Tactical"]


class Palette:
    def __init__(self):
        self.item_rects = {}
        self._build_rects()

    def _build_rects(self):
        spacing = WIDTH // (len(PALETTE_ITEMS) + 1)
        y = HEIGHT - PALETTE_HEIGHT // 2
        for i, name in enumerate(PALETTE_ITEMS):
            x = spacing * (i + 1)
            self.item_rects[name] = pygame.Rect(x - 30, y - 18, 60, 36)

    @property
    def top(self):
        return HEIGHT - PALETTE_HEIGHT

    def hit_test(self, mx, my):
        for name, rect in self.item_rects.items():
            if rect.collidepoint(mx, my):
                return name
        return None

    def draw(self, surf, inventory=None, font=None):
        # Background
        bg_rect = pygame.Rect(0, self.top, WIDTH, PALETTE_HEIGHT)
        pygame.draw.rect(surf, PALETTE_BG, bg_rect)
        pygame.draw.line(surf, (50, 50, 70), (0, self.top), (WIDTH, self.top), 2)

        for name, rect in self.item_rects.items():
            count = inventory.count(name) if inventory else 0
            color = COMPONENT_COLORS.get(name, (150, 150, 150))
            if count <= 0:
                color = MUTED

            pygame.draw.rect(surf, color, rect, border_radius=8)

            if font:
                # Component letter
                label = font.render(name[0], True, (255, 255, 255))
                surf.blit(label, (rect.centerx - label.get_width() // 2,
                                  rect.centery - label.get_height() // 2 - 6))
                # Count badge
                count_text = font.render(str(count), True, TEXT_COLOR)
                surf.blit(count_text, (rect.centerx - count_text.get_width() // 2,
                                       rect.centery + 4))
                # Name below
                name_text = font.render(name, True, MUTED)
                surf.blit(name_text, (rect.centerx - name_text.get_width() // 2,
                                      rect.bottom + 2))
