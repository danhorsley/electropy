from game.settings import (
    ENTROPY_MAX, WIRE_PROPAGATION_RATE, BASE_ENTROPY_GROWTH,
    SOURCE_ENTROPY_MULTIPLIER, GROUND_DRAIN_RATE,
)
from game.entities.component import Resistor, Capacitor, Diode


def tick(nodes, wires, dt):
    # 1. Base entropy growth per node
    for node in nodes:
        growth = BASE_ENTROPY_GROWTH * node.entropy_rate * dt
        # Source nodes generate entropy much faster
        if node.is_source:
            growth *= SOURCE_ENTROPY_MULTIPLIER
        # Resistors reduce growth
        for comp in node.components:
            if isinstance(comp, Resistor):
                growth *= comp.reduction
        node.entropy = min(ENTROPY_MAX, node.entropy + growth)

    # 2. Ground drain — proportional to ground's entropy (drains faster when hotter)
    for node in nodes:
        if node.is_ground:
            drain = GROUND_DRAIN_RATE * (node.entropy / ENTROPY_MAX) * dt
            node.entropy = max(0.0, node.entropy - drain)

    # 3. Wire propagation (entropy equalizes like heat diffusion)
    for wire in wires:
        a, b = wire.node_a, wire.node_b
        diff = a.entropy - b.entropy

        # Check for diode restriction
        if wire.diode:
            allowed_from = wire.diode.allowed_from
            # Only allow flow in the permitted direction
            if diff > 0 and a is not allowed_from:
                continue
            if diff < 0 and b is not allowed_from:
                continue

        flow = diff * WIRE_PROPAGATION_RATE * dt * 0.1  # damped
        a.entropy -= flow
        b.entropy += flow

    # 4. Component effects (capacitors, transistors tick their own state)
    for node in nodes:
        for comp in node.components:
            comp.apply(dt)

    # Also tick wire-attached components (diodes)
    for wire in wires:
        if wire.diode:
            wire.diode.apply(dt)

    # 5. Clamp and track peaks
    for node in nodes:
        node.entropy = max(0.0, min(ENTROPY_MAX, node.entropy))
        if node.entropy > node.peak_entropy:
            node.peak_entropy = node.entropy
