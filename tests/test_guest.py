from sim.guest import Guest, GuestState
from sim.park import Park
from sim.tiles import TileType
from sim.constants import HUNGER_THRESHOLD

def make_park_with_path():
    park = Park()
    for col in range(park.width):
        park.set_tile(park.height - 1, col, TileType.PATH)
    park.set_tile(park.height - 1, park.width // 2, TileType.ENTRANCE)
    park.flow_field.recompute(park.grid)
    return park

def test_guest_constructs():
    guest = Guest()
    assert guest.state == GuestState.WANDERING
    assert 0.0 <= guest.hunger < 0.3
    assert guest.money > 0

def test_guest_wanders():
    park = make_park_with_path()
    guest = Guest()
    initial_row = guest.row
    initial_col = guest.col
    guest.update(park)
    assert (guest.row, guest.col) != (initial_row, initial_col) or guest.state == GuestState.WANDERING

def test_guest_gets_hungry():
    park = make_park_with_path()
    guest = Guest()
    guest.hunger = HUNGER_THRESHOLD - 0.001
    guest.update(park)
    assert guest.state == GuestState.HUNGRY

def test_guest_finds_food():
    park = make_park_with_path()
    guest = Guest(row=park.height - 1, col=park.width // 2)
    park.set_tile(park.height - 1, park.width // 2 + 1, TileType.STALL)
    guest.state = GuestState.HUNGRY
    guest.hunger = HUNGER_THRESHOLD
    initial_money = guest.money
    guest.update(park)
    assert guest.state == GuestState.WANDERING
    assert guest.hunger == 0.0
    assert guest.money == initial_money - 5.0

def test_guest_exits_when_broke():
    park = make_park_with_path()
    guest = Guest()
    guest.state = GuestState.HUNGRY
    guest.money = 0.0
    guest.update(park)
    assert guest.state == GuestState.EXITING

def test_guest_reaches_exit():
    park = make_park_with_path()
    guest = Guest(row=park.height - 1, col=park.width // 2)
    guest.state = GuestState.EXITING
    guest.update(park)
    assert guest.state == GuestState.LEFT

def test_park_removes_left_guests():
    park = make_park_with_path()
    guest = Guest(row=park.height - 1, col=park.width // 2)
    guest.state = GuestState.LEFT
    park.guests.append(guest)
    park.tick()
    assert guest not in park.guests