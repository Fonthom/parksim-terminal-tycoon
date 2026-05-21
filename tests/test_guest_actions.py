from sim.guest_actions import find_adjacent_facility
from sim.tiles import TileType
from sim.park import Park
from sim.guest import Guest
from sim.guest_actions import ride
from sim.constants import RIDE_PRICE
from sim.guest_state import GuestState
from sim.constants import RIDE_PRICE
from sim.guest_actions import find_food, find_adjacent_facility
from sim.guest_actions import find_toilet
from sim.guest_actions import walk_toward_exit
from sim.guest_actions import pick_ride_target


def make_park_and_guest():
    park  = Park()
    mid   = park.width // 2
    guest = Guest(row=park.height - 2, col=mid, money=50.0)
    return park, guest
 
def test_ride_deducts_money_and_adds_happiness():
    park, guest = make_park_and_guest()
    initial_money     = guest.money
    initial_happiness = guest.happiness
    ride_pos = (0, 0)
    ride(guest, park, ride_pos)
    assert guest.money     == initial_money - RIDE_PRICE
    assert guest.happiness >  initial_happiness
    assert ride_pos in guest.visited_rides
 
def test_ride_exits_if_no_money():
    park, guest = make_park_and_guest()
    guest.money = 0.0
    ride(guest, park, (0, 0))
    assert guest.state == GuestState.EXITING
 
def test_ride_earns_income_for_park():
    park, guest = make_park_and_guest()
    ride(guest, park, (0, 0))
    assert park.finance.accumulated_income >= RIDE_PRICE
 
def test_find_food_resets_hunger_when_adjacent():
    park, guest = make_park_and_guest()
    mid = park.width // 2
    stall_row = park.height - 2
    stall_col = mid + 1
    park.grid[park.to_index(stall_row, stall_col)] = TileType.STALL
    guest.hunger = 0.8
    find_food(guest, park)
    assert guest.hunger == 0.0
 
def test_find_toilet_resets_bladder_when_adjacent():
    park, guest = make_park_and_guest()
    mid = park.width // 2
    toilet_row = park.height - 2
    toilet_col = mid + 1
    park.grid[park.to_index(toilet_row, toilet_col)] = TileType.TOILET
    guest.bladder = 0.9
    find_toilet(guest, park)
    assert guest.bladder == 0.0
    assert guest.state   == GuestState.WANDERING
 
def test_walk_toward_exit_sets_left_at_entrance():
    park, guest = make_park_and_guest()
    mid = park.width // 2
    guest.row = park.height - 1
    guest.col = mid
    walk_toward_exit(guest, park)
    assert guest.state == GuestState.LEFT
 
def test_pick_ride_target_returns_unvisited():
    park, guest = make_park_and_guest()
    target = pick_ride_target(guest, park)
    assert target is not None
    assert park.get_tile(target[0], target[1]) == TileType.RIDE
 
def test_pick_ride_target_returns_none_when_all_visited():
    park, guest = make_park_and_guest()
    for row in range(park.height):
        for col in range(park.width):
            if park.get_tile(row, col) == TileType.RIDE:
                guest.visited_rides.add((row, col))
    target = pick_ride_target(guest, park)
    assert target is None
 
def test_find_adjacent_facility_finds_stall():
    park, guest = make_park_and_guest()
    mid = park.width // 2
    stall_col = mid + 1
    park.grid[park.to_index(park.height - 2, stall_col)] = TileType.STALL
    result = find_adjacent_facility(guest, park, TileType.STALL)
    assert result == (park.height - 2, stall_col)
 
def test_find_adjacent_facility_skips_visited_rides():
    park, guest = make_park_and_guest()
    mid = park.width // 2
    ride_col = mid + 1
    park.grid[park.to_index(park.height - 2, ride_col)] = TileType.RIDE
    guest.visited_rides.add((park.height - 2, ride_col))
    result = find_adjacent_facility(guest, park, TileType.RIDE)
    assert result != (park.height - 2, ride_col)