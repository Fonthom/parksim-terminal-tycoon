from .tiles import TileType
from .constants import (
    BUILD_COST_PATH, BUILD_COST_RIDE, BUILD_COST_STALL, BUILD_COST_TOILET,
    DEMOLISH_COST_PATH, DEMOLISH_COST_RIDE, DEMOLISH_COST_STALL, DEMOLISH_COST_TOILET
)

BUILD_COSTS = {
    TileType.PATH:   BUILD_COST_PATH,
    TileType.RIDE:   BUILD_COST_RIDE,
    TileType.STALL:  BUILD_COST_STALL,
    TileType.TOILET: BUILD_COST_TOILET,
    TileType.GRASS:  0.0,
}

DEMOLISH_COSTS = {
    TileType.PATH:   DEMOLISH_COST_PATH,
    TileType.RIDE:   DEMOLISH_COST_RIDE,
    TileType.STALL:  DEMOLISH_COST_STALL,
    TileType.TOILET: DEMOLISH_COST_TOILET,
    TileType.GRASS:  0.0,
    TileType.ENTRANCE: 0.0,
}

def build_cost(tile_type: TileType) -> float:
    return BUILD_COSTS.get(tile_type, 0.0)

def demolish_cost(tile_type: TileType) -> float:
    return DEMOLISH_COSTS.get(tile_type, 0.0)

def try_place_tile(park, row, col, tile_type: TileType) -> bool:
    if park.get_tile(row, col) == TileType.ENTRANCE:
        return False
    cost = build_cost(tile_type)
    if cost > 0 and not park.finance.spend(cost):
        return False
    park.grid[park.to_index(row, col)] = tile_type
    park._recompute_fields()
    return True

def try_demolish_tile(park, row, col) -> bool:
    current = park.get_tile(row, col)
    if current in (TileType.GRASS, TileType.ENTRANCE):
        return False
    cost = demolish_cost(current)
    if cost > 0 and not park.finance.spend(cost):
        return False
    park.grid[park.to_index(row, col)] = TileType.GRASS
    park._recompute_fields()
    return True