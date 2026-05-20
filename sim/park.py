import random
from typing import List
from dataclasses import dataclass, field
from .constants import PARK_WIDTH, PARK_HEIGHT, MAX_GUESTS, SPAWN_RATE
from .tiles import TileType
from .guest import Guest
from .guest_state import GuestState
from .finance import Finance
from .flow_field import FlowField
from .layout import build_default_layout
from .building import try_place_tile, try_demolish_tile

@dataclass
class Park:
    width: int        = PARK_WIDTH
    height: int       = PARK_HEIGHT
    grid: List[TileType] = field(default_factory=lambda: [TileType.GRASS] * (PARK_WIDTH * PARK_HEIGHT))
    guests: List[Guest]  = field(default_factory=list)
    finance: Finance     = field(default_factory=Finance)
    food_field:   FlowField = field(default_factory=FlowField)
    toilet_field: FlowField = field(default_factory=FlowField)
    exit_field:   FlowField = field(default_factory=FlowField)

    def __post_init__(self):
        build_default_layout(self)
        self._recompute_fields()

    def tick(self):
        self.finance.game_tick(self)
        self._spawn_guests()
        for guest in self.guests:
            guest.update(self)
        self.guests = [g for g in self.guests if g.state != GuestState.LEFT]

    def get_tile(self, row, col) -> TileType:
        return self.grid[self.to_index(row, col)]

    def to_index(self, row, col) -> int:
        return row * self.width + col

    def is_within_bounds(self, row, col) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def is_occupied(self, row, col) -> bool:
        return any(g.row == row and g.col == col for g in self.guests)

    def place_tile(self, row, col, tile_type: TileType) -> bool:
        return try_place_tile(self, row, col, tile_type)

    def demolish_tile(self, row, col) -> bool:
        return try_demolish_tile(self, row, col)

    def _recompute_fields(self):
        self.food_field.recompute_for_food(self.grid)
        self.toilet_field.recompute_for_toilet(self.grid)
        self.exit_field.recompute_for_exit(self.grid)

    def _spawn_guests(self):
        spawn_row = self.height - 2
        spawn_col = self.width // 2
        if len(self.guests) < MAX_GUESTS and random.random() < SPAWN_RATE:
            if not self.is_occupied(spawn_row, spawn_col):
                entrance_fee = self.finance.entrance_fee
                guest = Guest(row=spawn_row, col=spawn_col)
                guest.money -= entrance_fee
                self.finance.earn(entrance_fee)
                self.guests.append(guest)

def run():
    park = Park()
    while not park.finance.is_bankrupt():
        park.tick()