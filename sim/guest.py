import random
from dataclasses import dataclass, field
from .tiles import TileType
from .guest_state import GuestState
from .constants import (
    PARK_WIDTH, PARK_HEIGHT,
    HUNGER_THRESHOLD, HUNGER_RATE,
    BLADDER_RATE, BLADDER_RATE_AFTER_EATING, BLADDER_THRESHOLD,
    HAPPINESS_EXIT_THRESHOLD,
    RIDE_COST, STALL_COST
)

@dataclass
class Guest:
    row: int = PARK_HEIGHT - 2
    col: int = PARK_WIDTH // 2
    state: GuestState = GuestState.WANDERING
    hunger: float = field(default_factory=lambda: random.uniform(0.0, 0.3))
    happiness: float = 1.0
    money: float = field(default_factory=lambda: random.uniform(20.0, 80.0))
    bladder: float = field(default_factory=lambda: random.uniform(0.0, 0.2))
    bladder_rate: float = BLADDER_RATE
    visited_rides: set = field(default_factory=set)
    target: tuple = field(default=None)

    def update(self, park):
        if self.state == GuestState.WANDERING:
            self._wander(park)
        elif self.state == GuestState.HUNGRY:
            self._find_food(park)
        elif self.state == GuestState.NEED_TOILET:
            self._find_toilet(park)
        elif self.state == GuestState.EXITING:
            self._walk_toward_exit(park)

    # --- needs ---

    def _tick_needs(self):
        self.hunger += HUNGER_RATE
        self.bladder += self.bladder_rate

    def _check_bladder_accident(self):
        if self.bladder >= 1.0:
            self.bladder = 0.0
            self.happiness = 0.0

    def _check_should_exit(self):
        if self.money <= 0 or self.happiness <= HAPPINESS_EXIT_THRESHOLD:
            self.state = GuestState.EXITING
            self.target = None
            return True
        return False

    # --- states ---

    def _wander(self, park):
        self._tick_needs()
        self._check_bladder_accident()

        if self._check_should_exit():
            return
        if self.bladder >= BLADDER_THRESHOLD:
            self.state = GuestState.NEED_TOILET
            self.target = None
            return
        if self.hunger >= HUNGER_THRESHOLD:
            self.state = GuestState.HUNGRY
            self.target = None
            return

        if self.target is None or self.target in self.visited_rides:
            self.target = self._pick_ride_target(park)

        ride_pos = self._find_adjacent_facility(park, TileType.RIDE)
        if ride_pos:
            self._ride(park, ride_pos)
        elif self.target:
            self._move_toward_target(park, self.target)
        else:
            self._move_random(park)

    def _ride(self, park, ride_pos):
        if self.money < RIDE_COST:
            self.state = GuestState.EXITING
            self.target = None
            return
        self.money -= RIDE_COST
        self.happiness = min(1.0, self.happiness + 0.2)
        self.visited_rides.add(ride_pos)
        self.target = None

    def _find_food(self, park):
        self._tick_needs()
        self._check_bladder_accident()

        if self._check_should_exit():
            return

        stall_pos = self._find_adjacent_facility(park, TileType.STALL)
        if stall_pos:
            self.hunger = 0.0
            self.money -= STALL_COST
            self.bladder_rate = BLADDER_RATE_AFTER_EATING
            self.state = GuestState.WANDERING
        else:
            self._move_with_field(park, park.food_field)

    def _find_toilet(self, park):
        self._tick_needs()
        self._check_bladder_accident()

        if self._check_should_exit():
            return

        toilet_pos = self._find_adjacent_facility(park, TileType.TOILET)
        if toilet_pos:
            self.bladder = 0.0
            self.bladder_rate = BLADDER_RATE
            self.state = GuestState.WANDERING
        else:
            self._move_with_field(park, park.toilet_field)

    def _walk_toward_exit(self, park):
        if park.get_tile(self.row, self.col) == TileType.ENTRANCE:
            self.state = GuestState.LEFT
            return
        row_delta, col_delta = park.exit_field.get_direction(self.row, self.col)
        if (row_delta, col_delta) == (0, 0):
            self._move_random(park)
            return
        new_row = self.row + row_delta
        new_col = self.col + col_delta
        if park.is_within_bounds(new_row, new_col):
            self.row = new_row
            self.col = new_col

    # --- movement ---

    def _move_toward_target(self, park, target):
        tr, tc = target
        candidates = []
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = self.row + row_delta
            nc = self.col + col_delta
            if not park.is_within_bounds(nr, nc):
                continue
            if park.get_tile(nr, nc) not in {TileType.PATH, TileType.ENTRANCE}:
                continue
            dist = abs(nr - tr) + abs(nc - tc)
            candidates.append((dist, nr, nc))
        if not candidates:
            self._move_random(park)
            return
        candidates.sort()
        best_dist = candidates[0][0]
        best = [c for c in candidates if c[0] == best_dist]
        _, nr, nc = random.choice(best)
        self.row = nr
        self.col = nc

    def _move_with_field(self, park, field):
        row_delta, col_delta = field.get_direction(self.row, self.col)
        if (row_delta, col_delta) == (0, 0):
            self._move_random(park)
            return
        new_row = self.row + row_delta
        new_col = self.col + col_delta
        if park.is_within_bounds(new_row, new_col):
            self.row = new_row
            self.col = new_col

    def _move_random(self, park):
        walkable = []
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = self.row + row_delta
            nc = self.col + col_delta
            if not park.is_within_bounds(nr, nc):
                continue
            if park.get_tile(nr, nc) in {TileType.PATH, TileType.ENTRANCE}:
                walkable.append((nr, nc))
        if walkable:
            self.row, self.col = random.choice(walkable)

    # --- helpers ---

    def _pick_ride_target(self, park) -> tuple | None:
        unvisited = [
            (row, col)
            for row in range(park.height)
            for col in range(park.width)
            if park.get_tile(row, col) == TileType.RIDE
            and (row, col) not in self.visited_rides
        ]
        return random.choice(unvisited) if unvisited else None

    def _find_adjacent_facility(self, park, tile_type) -> tuple | None:
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = self.row + row_delta
            nc = self.col + col_delta
            if not park.is_within_bounds(nr, nc):
                continue
            if park.get_tile(nr, nc) == tile_type:
                pos = (nr, nc)
                if tile_type == TileType.RIDE and pos in self.visited_rides:
                    continue
                return pos
        return None