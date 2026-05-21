from sim.park import Park
from sim.tiles import TileType


def test_layout_places_entrance():
    park = Park()
    mid  = park.width // 2
    assert park.get_tile(park.height - 1, mid) == TileType.ENTRANCE
 
def test_layout_places_rides():
    park  = Park()
    rides = [(r, c) for r in range(park.height) for c in range(park.width) if park.get_tile(r, c) == TileType.RIDE]
    assert len(rides) >= 3
 
def test_layout_places_stalls():
    park   = Park()
    stalls = [(r, c) for r in range(park.height) for c in range(park.width) if park.get_tile(r, c) == TileType.STALL]
    assert len(stalls) >= 1
 
def test_layout_places_toilets():
    park    = Park()
    toilets = [(r, c) for r in range(park.height) for c in range(park.width) if park.get_tile(r, c) == TileType.TOILET]
    assert len(toilets) >= 1
 
def test_layout_bottom_row_is_path():
    park = Park()
    for col in range(park.width):
        tile = park.get_tile(park.height - 1, col)
        assert tile in {TileType.PATH, TileType.ENTRANCE}
 
def test_layout_rides_adjacent_to_path():
    park = Park()
    for row in range(park.height):
        for col in range(park.width):
            if park.get_tile(row, col) == TileType.RIDE:
                neighbours = [
                    park.get_tile(row + dr, col + dc)
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]
                    if park.is_within_bounds(row + dr, col + dc)
                ]
                assert TileType.PATH in neighbours or TileType.ENTRANCE in neighbours