from sim.guest_movement import move_random
from sim.guest import Guest
from sim.park import Park
from sim.tiles import TileType
from sim.guest_movement import move_toward_target
from sim.guest_movement import move_with_field


def make_simple_park():
    return Park()
 
def test_move_random_stays_on_walkable():
    park = make_simple_park()
    mid = park.width // 2
    g = Guest(row=park.height - 2, col=mid)
    for _ in range(20):
        move_random(g, park)
        tile = park.get_tile(g.row, g.col)
        assert tile in {TileType.PATH, TileType.ENTRANCE}
 
def test_move_toward_target_reduces_distance():
    park = make_simple_park()
    mid = park.width // 2
    g = Guest(row=park.height - 2, col=mid)
    target = (2, mid)
    initial_dist = abs(g.row - target[0]) + abs(g.col - target[1])
    move_toward_target(g, park, target)
    new_dist = abs(g.row - target[0]) + abs(g.col - target[1])
    assert new_dist <= initial_dist
 
def test_move_with_field_follows_direction():
    park = make_simple_park()
    mid = park.width // 2
    g = Guest(row=park.height - 2, col=mid)
    initial_row = g.row
    move_with_field(g, park, park.exit_field)
    assert (g.row, g.col) != (initial_row, mid) or park.exit_field.get_direction(initial_row, mid) == (0, 0)
 
def test_move_random_does_not_go_out_of_bounds():
    park = make_simple_park()
    mid = park.width // 2
    g = Guest(row=park.height - 2, col=mid)
    for _ in range(50):
        move_random(g, park)
        assert park.is_within_bounds(g.row, g.col)
