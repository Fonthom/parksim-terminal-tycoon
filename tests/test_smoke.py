from sim.park import Park
from sim.tiles import TileType

def make_playable_park():
    park = Park()
    for col in range(park.width):
        park.set_tile(park.height - 1, col, TileType.PATH)
    park.set_tile(park.height - 1, park.width // 2, TileType.ENTRANCE)
    for row in range(park.height - 1):
        park.set_tile(row, park.width // 2, TileType.PATH)
    park.set_tile(5, park.width // 2, TileType.RIDE)
    park.set_tile(10, park.width // 2 + 2, TileType.STALL)
    park.finance.income_per_tick = 10.0
    return park

def test_smoke_500_ticks():
    park = make_playable_park()
    for tick in range(500):
        park.tick()
    assert park.finance.cash > 0
    assert len(park.guests) <= 200
    assert all(guest.row >= 0 for guest in park.guests)
    assert all(guest.col >= 0 for guest in park.guests)

def test_no_guests_out_of_bounds():
    park = make_playable_park()
    for _ in range(500):
        park.tick()
        for guest in park.guests:
            assert 0 <= guest.row < park.height
            assert 0 <= guest.col < park.width