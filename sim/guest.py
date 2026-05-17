from dataclasses import dataclass
from .guest_state import GuestState
from .constants import PARK_WIDTH, PARK_HEIGHT
import random

@dataclass
class Guest:
    row: int = PARK_HEIGHT - 1
    col: int = PARK_WIDTH // 2
    state: GuestState = GuestState.WANDERING
    hunger: float = field(default_factory=lambda: random.uniform(0.0, 0.3))
    happiness: float = 1.0
    money: float = field(default_factory=lambda: random.uniform(10.0, 50.0))

    def update(self, park):
        pass