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

    def __post_init__(self):
        self.set_tile(self.height - 1, self.width // 2, TileType.ENTRANCE)

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