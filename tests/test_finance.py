from sim.constants import UPKEEP_PER_RIDE, UPKEEP_PER_STALL, UPKEEP_PER_TOILET
from sim.tiles import TileType
from sim.constants import PARK_WIDTH, PARK_HEIGHT
from sim.finance import Finance
from sim.constants import STARTING_CASH
from sim.constants import ENTRANCE_FEE, RIDE_PRICE, STALL_PRICE, TOILET_PRICE
from sim.constants import STARTING_CASH, UPKEEP_PER_RIDE, UPKEEP_PER_STALL, UPKEEP_PER_TOILET
from sim.constants import INCOME_TICK_INTERVAL, STARTING_CASH



def make_mock_park(rides=1, stalls=1, toilets=1):
    grid = [TileType.GRASS] * (PARK_WIDTH * PARK_HEIGHT)
    grid[0] = TileType.RIDE   if rides   > 0 else TileType.GRASS
    grid[1] = TileType.STALL  if stalls  > 0 else TileType.GRASS
    grid[2] = TileType.TOILET if toilets > 0 else TileType.GRASS
 
    class MockPark:
        pass
    p = MockPark()
    p.grid = grid
    return p
 
def test_finance_constructs():
    f = Finance()
    assert f.cash              == STARTING_CASH
    assert f.accumulated_income == 0.0
    assert f.tick_counter       == 0
 
def test_finance_default_prices():
    f = Finance()
    assert f.entrance_fee  == ENTRANCE_FEE
    assert f.ride_price    == RIDE_PRICE
    assert f.stall_price   == STALL_PRICE
    assert f.toilet_price  == TOILET_PRICE
 
def test_finance_earn_accumulates():
    f = Finance()
    f.earn(100.0)
    f.earn(50.0)
    assert f.accumulated_income == 150.0
    assert f.cash == f.__class__.__dataclass_fields__['cash'].default
 
def test_finance_spend_deducts():
    f = Finance()
    result = f.spend(500.0)
    assert result is True
    assert f.cash == STARTING_CASH - 500.0
 
def test_finance_spend_fails_when_insufficient():
    f = Finance()
    f.cash = 10.0
    result = f.spend(100.0)
    assert result is False
    assert f.cash == 10.0
 
def test_finance_is_bankrupt():
    f = Finance()
    assert not f.is_bankrupt()
    f.cash = 0.0
    assert f.is_bankrupt()
    f.cash = -1.0
    assert f.is_bankrupt()
 
def test_finance_settle_adds_income_minus_upkeep():
    f = Finance()
    f.earn(500.0)
    park = make_mock_park(rides=1, stalls=1, toilets=1)
    f._settle(park)
    expected_upkeep = UPKEEP_PER_RIDE + UPKEEP_PER_STALL + UPKEEP_PER_TOILET
    assert f.cash == STARTING_CASH + 500.0 - expected_upkeep
    assert f.accumulated_income == 0.0
 
def test_finance_settle_resets_income():
    f = Finance()
    f.earn(200.0)
    park = make_mock_park(rides=0, stalls=0, toilets=0)
    f._settle(park)
    assert f.accumulated_income == 0.0
 
def test_finance_game_tick_settles_at_interval():
    f = Finance()
    f.earn(300.0)
    park = make_mock_park(rides=0, stalls=0, toilets=0)
    for _ in range(INCOME_TICK_INTERVAL - 1):
        f.game_tick(park)
    assert f.cash == STARTING_CASH
    f.game_tick(park)
    assert f.cash == STARTING_CASH + 300.0
    assert f.tick_counter == 0
 
def test_finance_seconds_until_settlement():
    f = Finance()
    assert f.seconds_until_next_settlement() == round(INCOME_TICK_INTERVAL * 0.1)
    f.tick_counter = 100
    assert f.seconds_until_next_settlement() == round((INCOME_TICK_INTERVAL - 100) * 0.1)
 
def test_finance_calculate_upkeep():
    f = Finance()
    park = make_mock_park(rides=2, stalls=3, toilets=1)
    from sim.tiles import TileType
    park.grid[3] = TileType.RIDE
    upkeep = f._calculate_upkeep(park)
    assert upkeep == 2 * UPKEEP_PER_RIDE + 1 * UPKEEP_PER_STALL + 1 * UPKEEP_PER_TOILET