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
    food_field: FlowField = field(default_factory=FlowField)
    toilet_field: FlowField = field(default_factory=FlowField)
    exit_field: FlowField = field(default_factory=FlowField)
    
    def __post_init__(self):
        self._build_default_layout()
        self.food_field.recompute_for_food(self.grid)
        self.toilet_field.recompute_for_toilet(self.grid)
        self.exit_field.recompute_for_exit(self.grid)


    def _build_default_layout(self):
        mid_col = self.width // 2
        mid_row = self.height // 2

        for col in range(self.width):
            self.grid[self.to_index(self.height - 1, col)] = TileType.PATH
        self.grid[self.to_index(self.height - 1, mid_col)] = TileType.ENTRANCE

        for row in range(1, self.height - 1):
            self.grid[self.to_index(row, mid_col)] = TileType.PATH

        for col in range(max(1, mid_col - 12), min(self.width - 1, mid_col + 13)):
            self.grid[self.to_index(mid_row, col)] = TileType.PATH

        for dr in (-3, 3):
            r = mid_row + dr
            for col in range(max(1, mid_col - 8), min(self.width - 1, mid_col + 9)):
                self.grid[self.to_index(r, col)] = TileType.PATH

        left_branch_col = max(2, mid_col - 10)
        for r in range(mid_row - 1, 3, -1):
            self.grid[self.to_index(r, left_branch_col + 4)] = TileType.PATH
        for c in range(left_branch_col, left_branch_col + 5):
            self.grid[self.to_index(3, c)] = TileType.PATH
        self.grid[self.to_index(3, left_branch_col)] = TileType.RIDE

        right_branch_col = min(self.width - 6, mid_col + 6)
        for r in range(mid_row - 1, 4, -1):
            self.grid[self.to_index(r, right_branch_col - 4)] = TileType.PATH
        for c in range(right_branch_col - 4, right_branch_col + 1):
            self.grid[self.to_index(4, c)] = TileType.PATH
        self.grid[self.to_index(4, right_branch_col)] = TileType.RIDE

        top_ride_row = 2
        for c in range(mid_col - 2, mid_col + 3):
            self.grid[self.to_index(top_ride_row + 1, c)] = TileType.PATH
        self.grid[self.to_index(top_ride_row, mid_col)] = TileType.RIDE

        left_ride_col = max(2, mid_col - 18)
        left_ride_row = mid_row - 4
        for c in range(min(left_ride_col, mid_col), max(left_ride_col, mid_col) + 1):
            self.grid[self.to_index(left_ride_row, c)] = TileType.PATH
        self.grid[self.to_index(left_ride_row, left_ride_col)] = TileType.RIDE

        right_ride_col = min(self.width - 3, mid_col + 18)
        right_ride_row = mid_row - 5
        for c in range(min(right_ride_col, mid_col), max(right_ride_col, mid_col) + 1):
            self.grid[self.to_index(right_ride_row, c)] = TileType.PATH
        self.grid[self.to_index(right_ride_row, right_ride_col)] = TileType.RIDE

        stalls = [ (mid_row, mid_col + 8), (mid_row - 3, mid_col - 6), (mid_row + 3, mid_col + 3) ]
        for (r, c) in stalls:
            if 0 <= r < self.height and 0 <= c < self.width:
                if c > mid_col:
                    for pc in range(mid_col + 1, c):
                        self.grid[self.to_index(r, pc)] = TileType.PATH
                else:
                    for pc in range(c + 1, mid_col):
                        self.grid[self.to_index(r, pc)] = TileType.PATH
                self.grid[self.to_index(r, c)] = TileType.STALL

        toilets = [ (self.height - 6, 3), (self.height - 8, self.width - 4) ]
        for (r, c) in toilets:
            if 0 <= r < self.height and 0 <= c < self.width:
                for pc in range(min(c, mid_col), max(c, mid_col) + 1):
                    self.grid[self.to_index(r, pc)] = TileType.PATH
                self.grid[self.to_index(r, c)] = TileType.TOILET

        plaza_toilet = (mid_row + 1, mid_col - 2)
        pr, pc = plaza_toilet
        if 0 <= pr < self.height and 0 <= pc < self.width:
            for rr in range(min(mid_row, pr), max(mid_row, pr) + 1):
                self.grid[self.to_index(rr, pc)] = TileType.PATH
            self.grid[self.to_index(pr, pc)] = TileType.TOILET
    
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
        self.food_field.recompute_for_food(self.grid)
        self.toilet_field.recompute_for_toilet(self.grid)
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