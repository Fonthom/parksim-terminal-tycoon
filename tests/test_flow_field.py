from sim.flow_field import FlowField
from sim.tiles import TileType
from sim.constants import PARK_WIDTH, PARK_HEIGHT, FLOW_FIELD_INFINITY

def make_empty_grid():
    return [TileType.GRASS] * (PARK_WIDTH * PARK_HEIGHT)

def to_index(row, col):
    return row * PARK_WIDTH + col

def test_flow_field_constructs():
    flow_field = FlowField()
    assert len(flow_field.directions) == PARK_WIDTH * PARK_HEIGHT

def test_default_directions_are_zero():
    flow_field = FlowField()
    assert all(direction == (0, 0) for direction in flow_field.directions)

def test_get_direction():
    flow_field = FlowField()
    assert flow_field.get_direction(0, 0) == (0, 0)

def test_recompute_no_goals():
    flow_field = FlowField()
    grid = make_empty_grid()
    flow_field.recompute(grid)
    assert all(direction == (0, 0) for direction in flow_field.directions)

def test_recompute_points_toward_ride():
    flow_field = FlowField()
    grid = make_empty_grid()

    grid[to_index(5, 5)] = TileType.RIDE
    grid[to_index(5, 4)] = TileType.PATH
    grid[to_index(5, 3)] = TileType.PATH

    flow_field.recompute(grid)

    assert flow_field.get_direction(5, 4) == (0, 1)
    assert flow_field.get_direction(5, 3) == (0, 1)

def test_recompute_points_toward_entrance():
    flow_field = FlowField()
    grid = make_empty_grid()

    grid[to_index(10, 10)] = TileType.ENTRANCE
    grid[to_index(9, 10)] = TileType.PATH
    grid[to_index(8, 10)] = TileType.PATH

    flow_field.recompute(grid)

    assert flow_field.get_direction(9, 10) == (1, 0)
    assert flow_field.get_direction(8, 10) == (1, 0)

def test_grass_tiles_have_no_direction():
    flow_field = FlowField()
    grid = make_empty_grid()

    grid[to_index(5, 5)] = TileType.RIDE
    grid[to_index(5, 4)] = TileType.PATH

    flow_field.recompute(grid)

    assert flow_field.get_direction(0, 0) == (0, 0)

def test_is_within_bounds():
    flow_field = FlowField()
    assert flow_field.is_within_bounds(0, 0)
    assert flow_field.is_within_bounds(PARK_HEIGHT - 1, PARK_WIDTH - 1)
    assert not flow_field.is_within_bounds(-1, 0)
    assert not flow_field.is_within_bounds(0, PARK_WIDTH)