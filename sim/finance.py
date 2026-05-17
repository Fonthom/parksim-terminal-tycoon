from dataclasses import dataclass
from .constants import STARTING_CASH

@dataclass
class Finance:
    cash = STARTING_CASH
    income_per_tick: float = 0.0
    upkeep_per_tick: float = 0.0

    def tick(self):
        self.cash += self.income_per_tick - self.upkeep_per_tick

    def is_bankrupt(self):
        return self.cash <= 0.0