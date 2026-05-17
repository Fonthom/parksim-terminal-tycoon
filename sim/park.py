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