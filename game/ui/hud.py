import pygame
from game.settings import WIDTH, HEIGHT, TEXT_COLOR, ACCENT, DANGER, SUCCESS, MUTED, TACTICAL_DURATION


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 26)
        self.font_large = pygame.font.SysFont(None, 36)
        self.font_title = pygame.font.SysFont(None, 48)

    def draw_playing(self, surf, level, inventory,
                     tactical_active=False, tactical_remaining=0.0):
        # Timer (top-left)
        t = max(0, level.time_remaining)
        color = DANGER if t < 10 else TEXT_COLOR
        timer_text = self.font_large.render(f"{t:.1f}s", True, color)
        surf.blit(timer_text, (20, 16))

        # Level name (top-center)
        name_text = self.font_large.render(level.name, True, ACCENT)
        surf.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 12))

        # Level description
        if level.description:
            desc_text = self.font.render(level.description, True, MUTED)
            surf.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, 40))

        # Manufacturing info (top-right)
        mfg = level.manufactures
        if isinstance(mfg, dict):
            mfg_label = "Forging: " + ", ".join(mfg.keys())
        elif mfg == "all":
            mfg_label = "Forging: All"
        else:
            mfg_label = f"Forging: {mfg}"
        mfg_text = self.font.render(mfg_label, True, MUTED)
        surf.blit(mfg_text, (WIDTH - mfg_text.get_width() - 20, 20))

        # Tactical mode indicator
        if tactical_active:
            # "TACTICAL" label
            tac_color = (100, 200, 255)
            tac_text = self.font_large.render("TACTICAL", True, tac_color)
            surf.blit(tac_text, (WIDTH // 2 - tac_text.get_width() // 2, 50))

            # Countdown bar
            bar_w = 200
            bar_h = 8
            bx = WIDTH // 2 - bar_w // 2
            by = 82
            pygame.draw.rect(surf, (40, 40, 60), (bx, by, bar_w, bar_h), border_radius=4)
            fill_ratio = tactical_remaining / TACTICAL_DURATION
            fill_w = int(bar_w * fill_ratio)
            if fill_w > 0:
                pygame.draw.rect(surf, tac_color, (bx, by, fill_w, bar_h), border_radius=4)

        # Hints
        hint_y = HEIGHT - 108
        hints = []
        if tactical_active:
            hints.append("Right-click to remove | ESC to cancel")
        else:
            hints.append("SPACE: Tactical | Right-click: Remove")
        for hint in hints:
            hint_surf = self.font.render(hint, True, MUTED)
            surf.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, hint_y))

    def draw(self, surf):
        pass

    def draw_overlay(self, surf, title, subtitle, color, options=None):
        overlay = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        title_surf = self.font_title.render(title, True, color)
        surf.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 200))

        sub_surf = self.font_large.render(subtitle, True, TEXT_COLOR)
        surf.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 260))

        buttons = {}
        if options:
            y = 340
            for label in options:
                btn_text = self.font_large.render(label, True, TEXT_COLOR)
                btn_rect = pygame.Rect(WIDTH // 2 - 100, y, 200, 44)
                pygame.draw.rect(surf, (60, 60, 80), btn_rect, border_radius=8)
                pygame.draw.rect(surf, ACCENT, btn_rect, 2, border_radius=8)
                surf.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2,
                                     btn_rect.centery - btn_text.get_height() // 2))
                buttons[label] = btn_rect
                y += 60
        return buttons

    def draw_score(self, surf, level, earned):
        lines = [
            f"Components used: {level.components_used}",
            f"Avg peak entropy: {sum(n.peak_entropy for n in level.nodes) / len(level.nodes):.0f}%",
            "",
        ]
        mfg = level.manufactures
        if isinstance(mfg, dict):
            items = ", ".join(f"{v}x {k}" for k, v in mfg.items())
            lines.append(f"Earned: {items}")
        elif mfg == "all":
            lines.append(f"Earned: {earned} of each type!")
        else:
            lines.append(f"Earned: {earned}x {mfg}")

        y = 300
        for line in lines:
            text = self.font.render(line, True, TEXT_COLOR)
            surf.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 28

    def draw_menu(self, surf, levels_unlocked, inventory):
        surf.fill((18, 18, 28))

        title = self.font_title.render("ELECTROPY", True, ACCENT)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        subtitle = self.font.render("Entropic Circuits", True, MUTED)
        surf.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 90))

        inv_y = 130
        inv_text = self.font.render("Inventory:", True, TEXT_COLOR)
        surf.blit(inv_text, (WIDTH // 2 - 120, inv_y))
        inv_y += 28
        for name in ["Resistor", "Capacitor", "Diode", "Transistor", "Wire", "Tactical"]:
            count = inventory.count(name)
            c = TEXT_COLOR if count > 0 else MUTED
            t = self.font.render(f"  {name}: {count}", True, c)
            surf.blit(t, (WIDTH // 2 - 120, inv_y))
            inv_y += 24

        return inv_y + 20
