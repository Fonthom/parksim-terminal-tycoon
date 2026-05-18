from dataclasses import dataclass, field
from .guest_state import GuestState
from .constants import PARK_WIDTH, PARK_HEIGHT, HUNGER_RATE, HUNGER_THRESHOLD
from .tiles import TileType
import random

@dataclass
class Guest:
    row: int = PARK_HEIGHT - 2
    col: int = PARK_WIDTH // 2
    state: GuestState = GuestState.WANDERING
    hunger: float = field(default_factory=lambda: random.uniform(0.0, 0.3))
    happiness: float = 1.0
    money: float = field(default_factory=lambda: random.uniform(10.0, 50.0))

    def update(self, park):
        if self.state == GuestState.WANDERING:
            self._wander(park)
        elif self.state == GuestState.HUNGRY:
            self._find_food(park)
        elif self.state == GuestState.EXITING:
            self._walk_toward_exit(park)
    
    def _wander(self, park):
        self.hunger += HUNGER_RATE
        if self.hunger >= HUNGER_THRESHOLD:
            self.state = GuestState.HUNGRY
        elif park.get_tile(self.row, self.col) == TileType.RIDE:
            self.happiness = min(1.0, self.happiness + 0.1)
            self.state = GuestState.EXITING
        else:
            self._move(park)
    
    def _find_food(self, park):
        if self._is_stall_adjacent(park):
            self.hunger = 0.0
            self.money -= 5.0
            self.state = GuestState.WANDERING
        elif self.money <= 0:
            self.state = GuestState.EXITING
        else:
            self._move(park)
    
    def _walk_toward_exit(self, park):
        from .tiles import TileType
        if park.get_tile(self.row, self.col) == TileType.ENTRANCE:
            self.state = GuestState.LEFT
        else:
            row_delta, col_delta = park.exit_field.get_direction(self.row, self.col)
            if (row_delta, col_delta) == (0, 0):
                return
            new_row = self.row + row_delta
            new_col = self.col + col_delta
            if park.exit_field.is_within_bounds(new_row, new_col):
                self.row = new_row
                self.col = new_col
    
    def _move(self, park):
        row_delta, col_delta = park.flow_field.get_direction(self.row, self.col)
        if (row_delta, col_delta) == (0, 0):
            return
        new_row = self.row + row_delta
        new_col = self.col + col_delta
        if park.flow_field.is_within_bounds(new_row, new_col):
            self.row = new_row
            self.col = new_col

    def _is_stall_adjacent(self, park):
        from .tiles import TileType
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbour_row = self.row + row_delta
            neighbour_col = self.col + col_delta
            if park.flow_field.is_within_bounds(neighbour_row, neighbour_col):
                if park.get_tile(neighbour_row, neighbour_col) == TileType.STALL:
                    return True
        return False

    