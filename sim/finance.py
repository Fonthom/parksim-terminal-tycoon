from dataclasses import dataclass

@dataclass
class Finance:
    cash: float
    income_per_tick: float
    expenses_per_tick: float

    def tick(self):
        pass

    def is_bankrupt(self):
        pass