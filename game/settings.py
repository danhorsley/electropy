WIDTH = 1000
HEIGHT = 700
FPS = 60

ENTROPY_MAX = 100.0
BASE_ENTROPY_GROWTH = 3.5  # entropy units per second at rate 1.0
WIRE_PROPAGATION_RATE = 8.0  # entropy units per second that flow between connected nodes

NODE_RADIUS = 14
NODE_SNAP_DIST = 50
WIRE_CLICK_DIST = 15

# Node types
SOURCE_ENTROPY_MULTIPLIER = 3.0
GROUND_DRAIN_RATE = 2.0  # max drain rate per second (proportional to ground entropy)
SOURCE_COLOR = (220, 160, 40)
GROUND_COLOR = (60, 120, 200)

PALETTE_HEIGHT = 90

# Colors
BG_COLOR = (18, 18, 28)
WIRE_COLOR = (60, 60, 90)
WIRE_HOT_COLOR = (200, 70, 50)
PALETTE_BG = (30, 30, 45)
TEXT_COLOR = (220, 220, 230)
ACCENT = (100, 200, 255)
DANGER = (255, 70, 60)
SUCCESS = (80, 220, 120)
MUTED = (100, 100, 120)

COMPONENT_COLORS = {
    "Resistor": (80, 190, 80),
    "Capacitor": (70, 140, 255),
    "Diode": (220, 90, 90),
    "Transistor": (210, 200, 50),
    "Wire": (180, 180, 200),
    "Tactical": (100, 180, 220),
}

# Tactical mode
TACTICAL_DURATION = 5.0

# Transistor cooldown in seconds
TRANSISTOR_COOLDOWN = 5.0

# Capacitor
CAPACITOR_THRESHOLD = 55.0
CAPACITOR_MAX_CHARGE = 30.0
CAPACITOR_ABSORB_RATE = 15.0  # per second
CAPACITOR_DISCHARGE_RATE = 5.0  # per second when full
