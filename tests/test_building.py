from sim.park import Park
from sim.tiles import TileType
from sim.constants import BUILD_COST_PATH, BUILD_COST_RIDE, BUILD_COST_STALL, BUILD_COST_TOILET
from sim.building import build_cost
from sim.building import demolish_cost
from sim.constants import DEMOLISH_COST_PATH, DEMOLISH_COST_RIDE
from sim.constants import BUILD_COST_PATH, STARTING_CASH
from sim.constants import STARTING_CASH
from sim.constants import BUILD_COST_PATH, DEMOLISH_COST_PATH, STARTING_CASH


def test_build_cost_returns_correct_values():
    assert build_cost(TileType.PATH)   == BUILD_COST_PATH
    assert build_cost(TileType.RIDE)   == BUILD_COST_RIDE
    assert build_cost(TileType.STALL)  == BUILD_COST_STALL
    assert build_cost(TileType.TOILET) == BUILD_COST_TOILET
    assert build_cost(TileType.GRASS)  == 0.0
 
def test_demolish_cost_returns_correct_values():
    assert demolish_cost(TileType.PATH)     == DEMOLISH_COST_PATH
    assert demolish_cost(TileType.RIDE)     == DEMOLISH_COST_RIDE
    assert demolish_cost(TileType.ENTRANCE) == 0.0
    assert demolish_cost(TileType.GRASS)    == 0.0
 
def test_try_place_tile_deducts_cost():
    park = Park()
    park.place_tile(5, 5, TileType.PATH)
    assert park.finance.cash < STARTING_CASH
 
def test_try_place_tile_sets_tile():
    park = Park()
    park.place_tile(5, 5, TileType.PATH)
    assert park.get_tile(5, 5) == TileType.PATH
 
def test_try_place_tile_fails_on_entrance():
    park = Park()
    mid  = park.width // 2
    result = park.place_tile(park.height - 1, mid, TileType.PATH)
    assert result is False
    assert park.get_tile(park.height - 1, mid) == TileType.ENTRANCE
    assert park.finance.cash == STARTING_CASH
 
def test_try_place_tile_fails_when_broke():
    park = Park()
    park.finance.cash = 0.0
    result = park.place_tile(5, 5, TileType.RIDE)
    assert result is False
 
def test_try_demolish_tile_removes_tile():
    park = Park()
    park.place_tile(5, 5, TileType.PATH)
    park.demolish_tile(5, 5)
    assert park.get_tile(5, 5) == TileType.GRASS
 
def test_try_demolish_tile_deducts_cost():
    park = Park()
    park.place_tile(5, 5, TileType.PATH)
    cash_after_build = park.finance.cash
    park.demolish_tile(5, 5)
    assert park.finance.cash == cash_after_build - DEMOLISH_COST_PATH
 
def test_try_demolish_grass_returns_false():
    park   = Park()
    result = park.demolish_tile(0, 0)
    assert result is False
 
def test_try_demolish_entrance_returns_false():
    park   = Park()
    mid    = park.width // 2
    result = park.demolish_tile(park.height - 1, mid)
    assert result is False