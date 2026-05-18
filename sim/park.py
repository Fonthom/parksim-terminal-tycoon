from typing import List, Set, Tuple
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
    food_field: FlowField = field(default_factory=FlowField)
    exit_field: FlowField = field(default_factory=FlowField)
    
    def __post_init__(self):
        self._build_default_layout()
        self.flow_field.recompute(self.grid)
        self.food_field.recompute_for_food(self.grid)
        self.exit_field.recompute_for_exit(self.grid)

    def _build_default_layout(self):
        mid_col = self.width // 2

        # bottom row path
        for col in range(self.width):
            self.grid[self.to_index(self.height - 1, col)] = TileType.PATH
        self.grid[self.to_index(self.height - 1, mid_col)] = TileType.ENTRANCE

        # main vertical path up the middle
        for row in range(self.height - 1):
            self.grid[self.to_index(row, mid_col)] = TileType.PATH

        # top ride — branch left, ride at tip
        for col in range(mid_col - 3, mid_col):
            self.grid[self.to_index(2, col)] = TileType.PATH
        self.grid[self.to_index(2, mid_col - 4)] = TileType.RIDE

        # bottom ride — branch right, ride at tip
        for col in range(mid_col + 1, mid_col + 4):
            self.grid[self.to_index(self.height - 5, col)] = TileType.PATH
        self.grid[self.to_index(self.height - 5, mid_col + 4)] = TileType.RIDE

        # stall — branch right from middle, stall at tip
        branch_row = self.height // 2
        for col in range(mid_col + 1, mid_col + 4):
            self.grid[self.to_index(branch_row, col)] = TileType.PATH
        self.grid[self.to_index(branch_row, mid_col + 4)] = TileType.STALL

        # toilet — branch left from lower third, toilet at tip
        toilet_row = self.height // 3 * 2
        for col in range(mid_col - 3, mid_col):
            self.grid[self.to_index(toilet_row, col)] = TileType.PATH
        self.grid[self.to_index(toilet_row, mid_col - 4)] = TileType.TOILET
    
    def tick(self):
        self.finance.tick()
        self._spawn_guests()

        for guest in self.guests:
            guest.update(self)

        self.guests = [g for g in self.guests if g.state != GuestState.LEFT]

    def get_tile(self, row, col):
        return self.grid[self.to_index(row, col)]

    def is_within_bounds(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def is_occupied(self, row, col, ignore_guest=None):
        if not self.is_within_bounds(row, col):
            return False
        for guest in self.guests:
            if guest is ignore_guest:
                continue
            if (guest.row, guest.col) == (row, col):
                return True
        return False

    def set_tile(self, row, col, tile_type):
        self.grid[self.to_index(row, col)] = tile_type
        self.flow_field.recompute(self.grid)
        self.food_field.recompute_for_food(self.grid)
        self.exit_field.recompute_for_exit(self.grid)   
    
    def to_index(self, row, col):
        return row * self.width + col
    
    def _spawn_guests(self):
        spawn_row = self.height - 2
        spawn_col = self.width // 2

        if len(self.guests) < MAX_GUESTS:
            if random.random() < SPAWN_RATE:
                if not self.is_occupied(spawn_row, spawn_col):
                    self.guests.append(Guest(row=spawn_row, col=spawn_col))

def run():
    park = Park()
    while not park.finance.is_bankrupt():
        park.tick()