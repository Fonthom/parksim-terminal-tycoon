import random
from dataclasses import dataclass, field
from .guest_state import GuestState
from .guest_needs import tick_needs, check_bladder_accident, check_should_exit
from .guest_movement import move_toward_target, move_random
from .guest_actions import ride, find_food, find_toilet, walk_toward_exit, pick_ride_target, find_adjacent_facility
from .tiles import TileType
from .constants import (
    PARK_WIDTH, PARK_HEIGHT,
    HUNGER_THRESHOLD, BLADDER_THRESHOLD,
    BLADDER_RATE
)

@dataclass
class Guest:
    row: int          = PARK_HEIGHT - 2
    col: int          = PARK_WIDTH // 2
    state: GuestState = GuestState.WANDERING
    hunger: float     = field(default_factory=lambda: random.uniform(0.0, 0.3))
    happiness: float  = 1.0
    money: float      = field(default_factory=lambda: random.uniform(20.0, 80.0))
    bladder: float    = field(default_factory=lambda: random.uniform(0.0, 0.2))
    bladder_rate: float = BLADDER_RATE
    visited_rides: set  = field(default_factory=set)
    target: tuple       = field(default=None)

    def update(self, park):
        if self.state == GuestState.WANDERING:
            self._wander(park)
        elif self.state == GuestState.HUNGRY:
            self._hungry(park)
        elif self.state == GuestState.NEED_TOILET:
            self._need_toilet(park)
        elif self.state == GuestState.EXITING:
            self._exiting(park)

    def _wander(self, park):
        tick_needs(self)
        check_bladder_accident(self)

        if check_should_exit(self):
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
            self.target = pick_ride_target(self, park)

        ride_pos = find_adjacent_facility(self, park, TileType.RIDE)
        if ride_pos:
            ride(self, park, ride_pos)
        elif self.target:
            move_toward_target(self, park, self.target)
        else:
            move_random(self, park)

    def _hungry(self, park):
        tick_needs(self)
        check_bladder_accident(self)
        if check_should_exit(self):
            return
        find_food(self, park)

    def _need_toilet(self, park):
        tick_needs(self)
        check_bladder_accident(self)
        if check_should_exit(self):
            return
        find_toilet(self, park)

    def _exiting(self, park):
        walk_toward_exit(self, park)