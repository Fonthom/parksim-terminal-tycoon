from dataclasses import dataclass
from .constants import CASH

@dataclass
class Finance:
    cash = CASH
    income_per_tick: float = 0.0
    expenses_per_tick: float = 0.0

    def tick(self):
        pass

    def is_bankrupt(self):
        pass