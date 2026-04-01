from game.entities.node import Node
from game.entities.wire import Wire
from game.settings import ENTROPY_MAX


class Level:
    def __init__(self, definition):
        self.name = definition["name"]
        self.survive_time = definition["survive_time"]
        self.manufactures = definition["manufactures"]
        self.base_output = definition["base_output"]
        self.max_output = definition["max_output"]
        self.starter = definition.get("starter", {})

        self.description = definition.get("description", "")

        # Build nodes (supports 3-tuple or 4-tuple with node_type)
        self.nodes = []
        for node_def in definition["nodes"]:
            if len(node_def) == 4:
                nx, ny, rate, ntype = node_def
            else:
                nx, ny, rate = node_def
                ntype = "regular"
            self.nodes.append(Node(nx, ny, entropy_rate=rate, node_type=ntype))

        # Build wires
        self.wires = []
        for ai, bi in definition["wires"]:
            self.wires.append(Wire(self.nodes[ai], self.nodes[bi]))

        # Set initial entropy
        for i, node in enumerate(self.nodes):
            node.entropy = definition.get("start_entropy", [0.0] * len(self.nodes))[i]

        self.time_remaining = self.survive_time
        self.components_used = 0

    @property
    def won(self):
        return self.time_remaining <= 0

    @property
    def lost(self):
        return any(n.overloaded for n in self.nodes)

    def tick(self, dt):
        if not self.won and not self.lost:
            self.time_remaining = max(0, self.time_remaining - dt)

    def performance_ratio(self):
        if self.lost:
            return 0.0
        avg_peak = sum(n.peak_entropy for n in self.nodes) / len(self.nodes)
        peak_score = max(0.0, 1.0 - avg_peak / ENTROPY_MAX)
        efficiency_score = max(0.0, 1.0 - self.components_used / 10.0)
        return min(1.0, 0.4 + 0.4 * peak_score + 0.2 * efficiency_score)

    def calculate_output(self):
        if self.lost:
            return 0
        ratio = self.performance_ratio()
        # Return a score from base_output to max_output based on performance
        return max(self.base_output, int(self.max_output * ratio))
