from sim.park import Park
from sim.tiles import TileType

def test_park_constructs():
    park = Park()
    assert park.width == 80
    assert park.height == 40
    assert len(park.grid) == 80 * 40

def test_entrance_placed():
    park = Park()
    assert park.get_tile(park.height - 1, park.width // 2) == TileType.ENTRANCE

def test_grid_default_grass():
    park = Park()
    grass_tiles = [t for t in park.grid if t == TileType.GRASS]
    assert len(grass_tiles) == (80 * 40) - 1

def test_set_and_get_tile():
    park = Park()
    park.set_tile(0, 0, TileType.PATH)
    assert park.get_tile(0, 0) == TileType.PATH

def test_tick_runs():
    park = Park()
    park.tick()

def test_finance_tick():
    park = Park()
    park.finance.income_per_tick = 10.0
    park.tick()
    assert park.finance.cash == 10010.0

def test_is_not_bankrupt_at_start():
    park = Park()
    assert not park.finance.is_bankrupt()