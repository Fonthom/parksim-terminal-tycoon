import random
from .tiles import TileType
from dataclasses import dataclass, field
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
    visited_rides: set[tuple[int, int]] = field(default_factory=set)
    recent_visits: dict[tuple[int, int], int] = field(default_factory=dict)
    post_visit_timer: int = 0

    def update(self, park):
        self._countdown_recent_visits()
        if self.state == GuestState.WANDERING:
            self._wander(park)
        elif self.state == GuestState.HUNGRY:
            self._find_food(park)
        elif self.state == GuestState.NEED_TOILET:
            self._find_toilet(park)
        elif self.state == GuestState.EXITING:
            self._walk_toward_exit(park)

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
            return True
        return False

    def _countdown_recent_visits(self):
        expired = []
        for pos, timer in list(self.recent_visits.items()):
            timer -= 1
            if timer <= 0:
                expired.append(pos)
            else:
                self.recent_visits[pos] = timer
        for pos in expired:
            del self.recent_visits[pos]

    def _mark_recent_visit(self, pos: tuple[int, int]):
        self.recent_visits[pos] = random.randint(20, 30)

    def _start_post_visit_wander(self):
        self.post_visit_timer = random.randint(8, 12)

    def _wander(self, park):
        if self.post_visit_timer > 0:
            self._tick_needs()
            self._check_bladder_accident()

            if self._check_should_exit():
                return

            self._move_random(park)
            self.post_visit_timer -= 1
            if self.post_visit_timer == 0 and self.bladder >= BLADDER_THRESHOLD:
                self.state = GuestState.NEED_TOILET
            return

        self._tick_needs()
        self._check_bladder_accident()

        if self._check_should_exit():
            return
        if self.bladder >= BLADDER_THRESHOLD:
            self.state = GuestState.NEED_TOILET
            return
        if self.hunger >= HUNGER_THRESHOLD:
            self.state = GuestState.HUNGRY
            return

        if random.random() < 0.3:
            self._move_random(park)
            return

        ride_pos = self._find_adjacent_facility(park, TileType.RIDE)
        if ride_pos:
            self._ride(park, ride_pos)
        else:
            self._move(park)

    def _ride(self, park, ride_pos):
        if self.money < RIDE_COST:
            self.state = GuestState.EXITING
            return
        self.money -= RIDE_COST
        self.happiness = min(1.0, self.happiness + 0.2)
        self.visited_rides.add(ride_pos)
        self._mark_recent_visit(ride_pos)
        self._start_post_visit_wander()
    
    def _find_food(self, park):
        from .tiles import TileType
        self._tick_needs()
        self._check_bladder_accident()

        if self._check_should_exit():
            return

        if park.get_tile(self.row, self.col) == TileType.STALL:
            self.hunger = 0.0
            self.money -= STALL_COST
            self.bladder_rate = BLADDER_RATE_AFTER_EATING
            self.state = GuestState.WANDERING
            self._mark_recent_visit((self.row, self.col))
            self._start_post_visit_wander()
            return

        stall_pos = self._find_adjacent_facility(park, TileType.STALL)
        if stall_pos:
            self.hunger = 0.0
            self.money -= STALL_COST
            self.bladder_rate = BLADDER_RATE_AFTER_EATING
            self.state = GuestState.WANDERING
            self._mark_recent_visit(stall_pos)
            self._start_post_visit_wander()
        else:
            self._move_with_field(park, park.food_field)

    def _find_toilet(self, park):
        from .tiles import TileType
        self._tick_needs()
        self._check_bladder_accident()

        if self._check_should_exit():
            return
        toilet_pos = self._find_adjacent_facility(park, TileType.TOILET)
        if toilet_pos:
            self.bladder = 0.0
            self.bladder_rate = BLADDER_RATE
            self.state = GuestState.WANDERING
            self._mark_recent_visit(toilet_pos)
            self._start_post_visit_wander()
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
            if not self._try_move(park, new_row, new_col):
                self._move_random(park)
    
    def _move(self, park):
        from .tiles import TileType
        row_delta, col_delta = park.flow_field.get_direction(self.row, self.col)

        # if flow field points toward a recently visited facility, pick a random walkable neighbour instead
        next_row = self.row + row_delta
        next_col = self.col + col_delta
        if (next_row, next_col) in self.recent_visits:
            self._move_random(park)
            return

        if (row_delta, col_delta) == (0, 0):
            return

        if not park.is_within_bounds(next_row, next_col):
            return

        next_tile = park.get_tile(next_row, next_col)
        if next_tile == TileType.RIDE and (next_row, next_col) in self.visited_rides:
            self._move_random(park)
            return
        if next_tile not in {TileType.PATH, TileType.ENTRANCE}:
            self._move_random(park)
            return

        if not self._try_move(park, next_row, next_col):
            self._move_random(park)

    def _move_random(self, park):
        current_tile = park.get_tile(self.row, self.col)
        allow_leave_facility = current_tile in {TileType.RIDE, TileType.STALL, TileType.TOILET}

        walkable = []
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbour_row = self.row + row_delta
            neighbour_col = self.col + col_delta
            if not park.is_within_bounds(neighbour_row, neighbour_col):
                continue
            tile = park.get_tile(neighbour_row, neighbour_col)
            if tile not in {TileType.PATH, TileType.ENTRANCE}:
                continue
            if not allow_leave_facility and self._is_next_to_recently_visited_facility(park, neighbour_row, neighbour_col):
                continue

            walkable.append((neighbour_row, neighbour_col))
        if walkable:
            row, col = random.choice(walkable)
            self._try_move(park, row, col)

    def _move_with_field(self, park, field):
        row_delta, col_delta = field.get_direction(self.row, self.col)
        next_row = self.row + row_delta
        next_col = self.col + col_delta
        if (next_row, next_col) in self.recent_visits:
            self._move_random(park)
            return
        if (row_delta, col_delta) == (0, 0):
            return
        if not park.is_within_bounds(next_row, next_col):
            return
        next_tile = park.get_tile(next_row, next_col)
        if next_tile == TileType.RIDE and (next_row, next_col) in self.visited_rides:
            self._move_random(park)
            return
        if next_tile not in {TileType.PATH, TileType.ENTRANCE}:
            self._move_random(park)
            return
        if not self._try_move(park, next_row, next_col):
            self._move_random(park)

    def _try_move(self, park, row, col):
        self.row = row
        self.col = col
        return True

    def _is_next_to_recently_visited_facility(self, park, row, col):
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbour_row = row + row_delta
            neighbour_col = col + col_delta
            if (neighbour_row, neighbour_col) in self.recent_visits:
                return True
        return False

    def _is_adjacent_to(self, park, tile_type):
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbour_row = self.row + row_delta
            neighbour_col = self.col + col_delta
            if park.flow_field.is_within_bounds(neighbour_row, neighbour_col):
                if park.get_tile(neighbour_row, neighbour_col) == tile_type:
                    return True
        return False
    
    def _find_adjacent_facility(self, park, tile_type):
        for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbour_row = self.row + row_delta
            neighbour_col = self.col + col_delta
            if park.flow_field.is_within_bounds(neighbour_row, neighbour_col):
                if park.get_tile(neighbour_row, neighbour_col) == tile_type:
                    facility_pos = (neighbour_row, neighbour_col)
                    if tile_type == TileType.RIDE and facility_pos in self.visited_rides:
                        continue
                    if facility_pos not in self.recent_visits:
                        return facility_pos
        return None

    