from dataclasses import dataclass, field
from .constants import (
    STARTING_CASH, INCOME_TICK_INTERVAL,
    ENTRANCE_FEE, RIDE_PRICE, STALL_PRICE,
    UPKEEP_PER_RIDE, UPKEEP_PER_STALL, UPKEEP_PER_TOILET
)

@dataclass
class Finance:
    cash: float               = STARTING_CASH
    accumulated_income: float = 0.0
    tick_counter: int         = 0
    entrance_fee: float       = ENTRANCE_FEE
    ride_price: float         = RIDE_PRICE
    stall_price: float        = STALL_PRICE

    def game_tick(self, park):
        self.tick_counter += 1
        if self.tick_counter >= INCOME_TICK_INTERVAL:
            self._settle(park)
            self.tick_counter = 0

    def _settle(self, park):
        upkeep = self._calculate_upkeep(park)
        self.cash += self.accumulated_income - upkeep
        self.accumulated_income = 0.0

    def _calculate_upkeep(self, park):
        from .tiles import TileType
        ride_count   = sum(1 for t in park.grid if t == TileType.RIDE)
        stall_count  = sum(1 for t in park.grid if t == TileType.STALL)
        toilet_count = sum(1 for t in park.grid if t == TileType.TOILET)
        return (
            ride_count   * UPKEEP_PER_RIDE +
            stall_count  * UPKEEP_PER_STALL +
            toilet_count * UPKEEP_PER_TOILET
        )

    def earn(self, amount: float):
        self.accumulated_income += amount

    def spend(self, amount: float) -> bool:
        if self.cash < amount:
            return False
        self.cash -= amount
        return True

    def is_bankrupt(self):
        return self.cash <= 0.0

    def seconds_until_next_settlement(self) -> int:
        ticks_remaining = INCOME_TICK_INTERVAL - self.tick_counter
        return round(ticks_remaining * 0.1)