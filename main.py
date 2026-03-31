import pygame
import sys
import random
import math

# ====================== CONFIG ======================
WIDTH, HEIGHT = 1000, 700
FPS = 60
BG_COLOR = (20, 20, 30)
NODE_RADIUS = 12
ENTROPY_MAX = 100.0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Entropy Circuit Proto")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# ====================== CLASSES ======================
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.entropy = 30.0 + random.uniform(0, 20)  # starting chaos
        self.connections = []  # list of other nodes

    def draw(self, surf):
        color = pygame.Color(255, int(255 * (1 - self.entropy / ENTROPY_MAX)), 50)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), NODE_RADIUS)
        # entropy bar
        bar_w = 40
        bar_h = 6
        pygame.draw.rect(surf, (80,80,80), (self.x - bar_w//2, self.y - 25, bar_w, bar_h))
        fill = int(bar_w * (self.entropy / ENTROPY_MAX))
        pygame.draw.rect(surf, (255, 60, 60), (self.x - bar_w//2, self.y - 25, fill, bar_h))

class Component:
    def __init__(self, name, x, y, color):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.attached_node = None  # or wire

    def draw(self, surf):
        rect = pygame.Rect(self.x-20, self.y-20, 40, 40)
        pygame.draw.rect(surf, self.color, rect, border_radius=8)
        text = font.render(self.name[0], True, (255,255,255))  # first letter
        surf.blit(text, (self.x-8, self.y-12))

# Simple simulation rules
def update_entropy(nodes, components):
    for node in nodes:
        # base entropy growth
        growth = 0.15 + random.uniform(0, 0.1)
        
        # Apply component effects (very basic for proto)
        for comp in components:
            if comp.attached_node == node:
                if comp.name == "Resistor":
                    growth *= 0.4  # slows it down
                elif comp.name == "Capacitor":
                    # temporary store: absorb then release later (simple version)
                    if node.entropy > 60:
                        node.entropy -= 8  # dump some
                elif comp.name == "Diode":
                    # one-way: reduce back-propagation (stub: just slight global damp if high)
                    if node.entropy > 70:
                        growth *= 0.7
                elif comp.name == "Transistor":
                    # aha moment: when high, it can trigger a dump to connected nodes
                    if node.entropy > 75 and random.random() < 0.05:
                        for conn in node.connections:
                            conn.entropy = max(0, conn.entropy - 25)  # sudden relief!
        
        node.entropy = min(ENTROPY_MAX, node.entropy + growth)

# ====================== SETUP ======================
nodes = [
    Node(200, 300), Node(400, 200), Node(600, 300),
    Node(400, 450), Node(800, 350)
]

# Connect some wires (bidirectional for simplicity)
nodes[0].connections = [nodes[1], nodes[3]]
nodes[1].connections = [nodes[0], nodes[2]]
nodes[2].connections = [nodes[1], nodes[4]]
nodes[3].connections = [nodes[0], nodes[4]]
nodes[4].connections = [nodes[2], nodes[3]]

components = []  # player will add these

# Starting components in palette (bottom bar)
palette = [
    Component("Resistor", 150, HEIGHT-60, (100, 200, 100)),
    Component("Capacitor", 300, HEIGHT-60, (80, 160, 255)),
    Component("Diode", 450, HEIGHT-60, (220, 100, 100)),
    Component("Transistor", 600, HEIGHT-60, (200, 200, 50))
]

selected_comp = None
survival_time = 0
running = True

# ====================== MAIN LOOP ======================
while running:
    dt = clock.tick(FPS) / 1000.0
    survival_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Check palette click
            for comp in palette:
                if abs(mx - comp.x) < 30 and abs(my - comp.y) < 30:
                    selected_comp = Component(comp.name, mx, my, comp.color)
                    break

            # Place on nearest node if dragging a component
            if selected_comp:
                for node in nodes:
                    if math.hypot(mx - node.x, my - node.y) < 50:
                        selected_comp.attached_node = node
                        components.append(selected_comp)
                        selected_comp = None
                        break

        elif event.type == pygame.MOUSEMOTION and selected_comp:
            selected_comp.x, selected_comp.y = event.pos

    # Update simulation
    update_entropy(nodes, components)

    # Check failure
    failed = any(n.entropy >= ENTROPY_MAX for n in nodes)

    # Draw
    screen.fill(BG_COLOR)

    # Draw wires
    for node in nodes:
        for conn in node.connections:
            if conn in nodes:  # safety
                color = (80, 80, 120) if node.entropy < 60 else (255, 80, 60)
                pygame.draw.line(screen, color, (node.x, node.y), (conn.x, conn.y), 6)

    # Draw nodes
    for node in nodes:
        node.draw(screen)

    # Draw placed components
    for comp in components:
        comp.draw(screen)

    # Draw palette
    for comp in palette:
        comp.draw(screen)
    pygame.draw.rect(screen, (50,50,70), (0, HEIGHT-100, WIDTH, 100))

    # UI text
    time_text = font.render(f"Survival: {int(survival_time)}s", True, (255,255,255))
    screen.blit(time_text, (20, 20))
    
    if failed:
        fail_text = font.render("CIRCUIT OVERLOAD - ENTROPY CRITICAL", True, (255, 50, 50))
        screen.blit(fail_text, (WIDTH//2 - 220, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False
    else:
        pygame.display.flip()

pygame.quit()
sys.exit()