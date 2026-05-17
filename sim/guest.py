from dataclasses import dataclass
from .guest_state import GuestState

@dataclass
class Guest:
    row: int
    col: int
    state: GuestState
    hunger: float
    happiness: float
    money: float

    def update(self, park):
        pass