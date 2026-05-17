from dataclasses import dataclass
from sim.constants import PARK_WIDTH, PARK_HEIGHT, FLOW_FIELD_INFINITY

@dataclass
class FlowField:
    width: int = PARK_WIDTH
    height: int = PARK_HEIGHT
    directions: list = field(default_factory=lambda: [(0, 0)] * (PARK_WIDTH * PARK_HEIGHT))

    def update_grid(self, grid):
        pass

    def get_direction(self, row, col):
        pass