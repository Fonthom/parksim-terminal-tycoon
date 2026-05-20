import random
from .tiles import TileType
from .guest_state import GuestState
from .guest_movement import move_toward_target, move_with_field, move_random
from .constants import (
    BLADDER_RATE, BLADDER_RATE_AFTER_EATING
)

def ride(guest, park, ride_pos):
    price = park.finance.ride_price
    if guest.money < price:
        guest.state = GuestState.EXITING
        guest.target = None
        return
    guest.money -= price
    park.finance.earn(price)
    guest.happiness = min(1.0, guest.happiness + 0.2)
    guest.visited_rides.add(ride_pos)
    guest.target = None

def find_food(guest, park):
    stall_pos = find_adjacent_facility(guest, park, TileType.STALL)
    if stall_pos:
        price = park.finance.stall_price
        guest.hunger = 0.0
        guest.money -= price
        park.finance.earn(price)
        guest.bladder_rate = BLADDER_RATE_AFTER_EATING
        guest.state = GuestState.WANDERING
    else:
        move_with_field(guest, park, park.food_field)

def find_toilet(guest, park):
    toilet_pos = find_adjacent_facility(guest, park, TileType.TOILET)
    if toilet_pos:
        guest.bladder = 0.0
        guest.bladder_rate = BLADDER_RATE
        guest.state = GuestState.WANDERING
    else:
        move_with_field(guest, park, park.toilet_field)

def walk_toward_exit(guest, park):
    if park.get_tile(guest.row, guest.col) == TileType.ENTRANCE:
        guest.state = GuestState.LEFT
        return
    row_delta, col_delta = park.exit_field.get_direction(guest.row, guest.col)
    if (row_delta, col_delta) == (0, 0):
        move_random(guest, park)
        return
    new_row = guest.row + row_delta
    new_col = guest.col + col_delta
    if park.is_within_bounds(new_row, new_col):
        guest.row = new_row
        guest.col = new_col

def pick_ride_target(guest, park) -> tuple | None:
    unvisited = [
        (row, col)
        for row in range(park.height)
        for col in range(park.width)
        if park.get_tile(row, col) == TileType.RIDE
        and (row, col) not in guest.visited_rides
    ]
    return random.choice(unvisited) if unvisited else None

def find_adjacent_facility(guest, park, tile_type) -> tuple | None:
    for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr = guest.row + row_delta
        nc = guest.col + col_delta
        if not park.is_within_bounds(nr, nc):
            continue
        if park.get_tile(nr, nc) == tile_type:
            pos = (nr, nc)
            if tile_type == TileType.RIDE and pos in guest.visited_rides:
                continue
            return pos
    return None