from sim.flow_field import FlowField
from sim.tiles import TileType
from sim.constants import PARK_WIDTH, PARK_HEIGHT


def make_empty_grid():
    return [TileType.GRASS] * (PARK_WIDTH * PARK_HEIGHT)
 
def to_index(row, col):
    return row * PARK_WIDTH + col
 
def test_flow_field_constructs():
    f = FlowField()
    assert f.width  == PARK_WIDTH
    assert f.height == PARK_HEIGHT
    assert len(f.directions) == PARK_WIDTH * PARK_HEIGHT
 
def test_default_directions_zero():
    f = FlowField()
    assert all(d == (0, 0) for d in f.directions)
 
def test_is_within_bounds():
    f = FlowField()
    assert     f.is_within_bounds(0, 0)
    assert     f.is_within_bounds(PARK_HEIGHT - 1, PARK_WIDTH - 1)
    assert not f.is_within_bounds(-1, 0)
    assert not f.is_within_bounds(0, PARK_WIDTH)
    assert not f.is_within_bounds(PARK_HEIGHT, 0)
 
def test_get_direction():
    f = FlowField()
    assert f.get_direction(0, 0) == (0, 0)
 
def test_recompute_no_goals_stays_zero():
    f = FlowField()
    grid = make_empty_grid()
    f.recompute_for_food(grid)
    assert all(d == (0, 0) for d in f.directions)
 
def test_recompute_for_food_points_toward_stall():
    f = FlowField()
    grid = make_empty_grid()
    grid[to_index(5, 5)] = TileType.STALL
    grid[to_index(5, 4)] = TileType.PATH
    grid[to_index(5, 3)] = TileType.PATH
    f.recompute_for_food(grid)
    assert f.get_direction(5, 4) == (0, 1)
    assert f.get_direction(5, 3) == (0, 1)
 
def test_recompute_for_toilet_points_toward_toilet():
    f = FlowField()
    grid = make_empty_grid()
    grid[to_index(10, 10)] = TileType.TOILET
    grid[to_index(9,  10)] = TileType.PATH
    grid[to_index(8,  10)] = TileType.PATH
    f.recompute_for_toilet(grid)
    assert f.get_direction(9,  10) == (1, 0)
    assert f.get_direction(8,  10) == (1, 0)
 
def test_recompute_for_exit_points_toward_entrance():
    f = FlowField()
    grid = make_empty_grid()
    grid[to_index(39, 40)] = TileType.ENTRANCE
    grid[to_index(38, 40)] = TileType.PATH
    grid[to_index(37, 40)] = TileType.PATH
    f.recompute_for_exit(grid)
    assert f.get_direction(38, 40) == (1, 0)
    assert f.get_direction(37, 40) == (1, 0)
 
def test_grass_tiles_have_no_direction():
    f = FlowField()
    grid = make_empty_grid()
    grid[to_index(5, 5)] = TileType.STALL
    grid[to_index(5, 4)] = TileType.PATH
    f.recompute_for_food(grid)
    assert f.get_direction(0, 0) == (0, 0)