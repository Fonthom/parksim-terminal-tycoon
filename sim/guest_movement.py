import random
from .tiles import TileType

WALKABLE = {TileType.PATH, TileType.ENTRANCE}

def move_toward_target(guest, park, target):
    tr, tc = target
    candidates = []
    for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr = guest.row + row_delta
        nc = guest.col + col_delta
        if not park.is_within_bounds(nr, nc):
            continue
        if park.get_tile(nr, nc) not in WALKABLE:
            continue
        dist = abs(nr - tr) + abs(nc - tc)
        candidates.append((dist, nr, nc))
    if not candidates:
        move_random(guest, park)
        return
    candidates.sort()
    best_dist = candidates[0][0]
    best = [c for c in candidates if c[0] == best_dist]
    _, nr, nc = random.choice(best)
    guest.row = nr
    guest.col = nc

def move_with_field(guest, park, field):
    row_delta, col_delta = field.get_direction(guest.row, guest.col)
    if (row_delta, col_delta) == (0, 0):
        move_random(guest, park)
        return
    new_row = guest.row + row_delta
    new_col = guest.col + col_delta
    if park.is_within_bounds(new_row, new_col):
        guest.row = new_row
        guest.col = new_col

def move_random(guest, park):
    walkable = []
    for row_delta, col_delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr = guest.row + row_delta
        nc = guest.col + col_delta
        if not park.is_within_bounds(nr, nc):
            continue
        if park.get_tile(nr, nc) in WALKABLE:
            walkable.append((nr, nc))
    if walkable:
        guest.row, guest.col = random.choice(walkable)