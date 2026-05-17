from dataclasses import dataclass

@dataclass
class FlowField:
    width: int
    height: int
    field: List[[float, float]]

    def update_grid(self, grid):
        pass

    def get_direction(self, row, col):
        pass