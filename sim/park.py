from typing import List
from dataclasses import dataclass, field
from .constants import PARK_WIDTH, PARK_HEIGHT, MAX_GUESTS, SPAWN_RATE
from .tiles import TileType
from .guest import Guest
from .guest_state import GuestState
from .finance import Finance
from .flow_field import FlowField
import random

@dataclass
class Park:
    width: int = PARK_WIDTH
    height: int = PARK_HEIGHT
    grid: List[TileType] = field(default_factory=lambda: [TileType.GRASS for _ in range(PARK_WIDTH * PARK_HEIGHT)])
    guests: List[Guest] = field(default_factory=list)
    finance: Finance = field(default_factory=Finance)
    flow_field: FlowField = field(default_factory=FlowField)
    exit_field: FlowField = field(default_factory=FlowField)
    
    def __post_init__(self):
        self._build_default_layout()
        self.flow_field.recompute(self.grid)
        self.exit_field.recompute_for_exit(self.grid)

    def _build_default_layout(self):
        mid_col = self.width // 2

        for col in range(self.width):
            self.grid[self.to_index(self.height - 1, col)] = TileType.PATH

        self.grid[self.to_index(self.height - 1, mid_col)] = TileType.ENTRANCE

        for row in range(self.height - 1):
            self.grid[self.to_index(row, mid_col)] = TileType.PATH

        self.grid[self.to_index(2, mid_col)] = TileType.RIDE

        self.grid[self.to_index(self.height - 5, mid_col)] = TileType.RIDE

        branch_row = self.height // 2
        for col in range(mid_col + 1, mid_col + 4):
            self.grid[self.to_index(branch_row, col)] = TileType.PATH
        self.grid[self.to_index(branch_row, mid_col + 4)] = TileType.STALL
    
    def tick(self):
        self.finance.tick()
        self._spawn_guests()
        for guest in self.guests:
            guest.update(self)
        self.guests = [g for g in self.guests if g.state != GuestState.LEFT]
    
    def get_tile(self, row, col):
        return self.grid[self.to_index(row, col)]

    def set_tile(self, row, col, tile_type):
        self.grid[self.to_index(row, col)] = tile_type
        self.flow_field.recompute(self.grid)
        self.exit_field.recompute_for_exit(self.grid)   
    
    def to_index(self, row, col):
        return row * self.width + col
    
    def _spawn_guests(self):
        if len(self.guests) < MAX_GUESTS:
            if random.random() < SPAWN_RATE:
                self.guests.append(Guest())

def run():
    park = Park()
    while not park.finance.is_bankrupt():
        park.tick()