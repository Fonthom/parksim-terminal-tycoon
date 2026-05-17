from sim.constants import PARK_WIDTH, PARK_HEIGHT
from dataclasses import dataclass

@dataclass
class Park:
    width: int
    height: int
    grid: List[TileType]
    guests: List[Guest]
    finance: Finance
    flow_field: FlowField

    def tick(self):
        pass
    
    def get_tile(self, row, col):
        pass

    def set_tile(self, row, col, tile_type):
        pass
    
    def to_index(self, row, col):
        pass

def run():
    park = Park(
        width=PARK_WIDTH,
        height=PARK_HEIGHT,)