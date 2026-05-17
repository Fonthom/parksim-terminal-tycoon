from typing import List

from .constants import PARK_WIDTH, PARK_HEIGHT
from .tiles import TileType
from .guest import Guest
from .finance import Finance
from .flow_field import FlowField

@dataclass
class Park:
    width: int = PARK_WIDTH
    height: int = PARK_HEIGHT
    grid: List[TileType] = field(default_factory=lambda: [TileType.GRASS for _ in range(PARK_WIDTH * PARK_HEIGHT)])
    guests: List[Guest] = field(default_factory=list)
    finance: Finance = field(default_factory=lambda: Finance())
    flow_field: FlowField = field(default_factory=lambda: FlowField())

    def tick(self):
        pass
    
    def get_tile(self, row, col):
        pass

    def set_tile(self, row, col, tile_type):
        pass
    
    def to_index(self, row, col):
        return row * self.width + col

def run():
    park = Park(
        width=PARK_WIDTH,
        height=PARK_HEIGHT,)