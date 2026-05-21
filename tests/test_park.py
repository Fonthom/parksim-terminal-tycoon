from sim.park import Park
from sim.constants import MAX_GUESTS
from sim.constants import PARK_WIDTH, PARK_HEIGHT
from sim.tiles import TileType
from sim.guest import Guest
from sim.guest_state import GuestState
from sim.constants import INCOME_TICK_INTERVAL, STARTING_CASH


def test_park_constructs():
    park = Park()
    assert park.width  == PARK_WIDTH
    assert park.height == PARK_HEIGHT
    assert len(park.grid) == PARK_WIDTH * PARK_HEIGHT
 
def test_park_to_index():
    park = Park()
    assert park.to_index(0, 0)   == 0
    assert park.to_index(1, 0)   == park.width
    assert park.to_index(0, 1)   == 1
    assert park.to_index(2, 3)   == 2 * park.width + 3
 
def test_park_is_within_bounds():
    park = Park()
    assert     park.is_within_bounds(0, 0)
    assert     park.is_within_bounds(park.height - 1, park.width - 1)
    assert not park.is_within_bounds(-1, 0)
    assert not park.is_within_bounds(0, park.width)
 
def test_park_get_tile():
    park = Park()
    mid  = park.width // 2
    assert park.get_tile(park.height - 1, mid) == TileType.ENTRANCE
 
def test_park_tick_runs():
    park = Park()
    for _ in range(10):
        park.tick()
 
def test_park_tick_removes_left_guests():
    park  = Park()
    guest = Guest(row=park.height - 2, col=park.width // 2, state=GuestState.LEFT)
    park.guests.append(guest)
    park.tick()
    assert guest not in park.guests
 
def test_park_spawn_guests():
    park = Park()
    for _ in range(100):
        park.tick()
    assert len(park.guests) > 0
 
def test_park_max_guests_not_exceeded():
    park = Park()
    for _ in range(500):
        park.tick()
    assert len(park.guests) <= MAX_GUESTS
 
def test_park_is_occupied():
    park  = Park()
    guest = Guest(row=5, col=5)
    park.guests.append(guest)
    assert     park.is_occupied(5, 5)
    assert not park.is_occupied(5, 6)
 
def test_park_finance_ticks():
    park = Park()
    park.finance.earn(1000.0)
    for _ in range(INCOME_TICK_INTERVAL):
        park.tick()
    assert park.finance.cash != STARTING_CASH
 
def test_park_smoke_500_ticks():
    park = Park()
    for _ in range(500):
        park.tick()
    assert len(park.guests) <= MAX_GUESTS
    assert all(park.is_within_bounds(g.row, g.col) for g in park.guests)