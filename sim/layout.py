from .tiles import TileType

def build_default_layout(park):
    mid_col = park.width // 2
    mid_row = park.height // 2

    for col in range(park.width):
        park.grid[park.to_index(park.height - 1, col)] = TileType.PATH
    park.grid[park.to_index(park.height - 1, mid_col)] = TileType.ENTRANCE

    for row in range(1, park.height - 1):
        park.grid[park.to_index(row, mid_col)] = TileType.PATH

    for col in range(max(1, mid_col - 12), min(park.width - 1, mid_col + 13)):
        park.grid[park.to_index(mid_row, col)] = TileType.PATH

    for dr in (-3, 3):
        r = mid_row + dr
        for col in range(max(1, mid_col - 8), min(park.width - 1, mid_col + 9)):
            park.grid[park.to_index(r, col)] = TileType.PATH

    left_branch_col = max(2, mid_col - 10)
    for r in range(mid_row - 1, 3, -1):
        park.grid[park.to_index(r, left_branch_col + 4)] = TileType.PATH
    for c in range(left_branch_col, left_branch_col + 5):
        park.grid[park.to_index(3, c)] = TileType.PATH
    park.grid[park.to_index(3, left_branch_col)] = TileType.RIDE

    right_branch_col = min(park.width - 6, mid_col + 6)
    for r in range(mid_row - 1, 4, -1):
        park.grid[park.to_index(r, right_branch_col - 4)] = TileType.PATH
    for c in range(right_branch_col - 4, right_branch_col + 1):
        park.grid[park.to_index(4, c)] = TileType.PATH
    park.grid[park.to_index(4, right_branch_col)] = TileType.RIDE

    top_ride_row = 2
    for c in range(mid_col - 2, mid_col + 3):
        park.grid[park.to_index(top_ride_row + 1, c)] = TileType.PATH
    park.grid[park.to_index(top_ride_row, mid_col)] = TileType.RIDE

    left_ride_col = max(2, mid_col - 18)
    left_ride_row = mid_row - 4
    for c in range(min(left_ride_col, mid_col), max(left_ride_col, mid_col) + 1):
        park.grid[park.to_index(left_ride_row, c)] = TileType.PATH
    park.grid[park.to_index(left_ride_row, left_ride_col)] = TileType.RIDE

    right_ride_col = min(park.width - 3, mid_col + 18)
    right_ride_row = mid_row - 5
    for c in range(min(right_ride_col, mid_col), max(right_ride_col, mid_col) + 1):
        park.grid[park.to_index(right_ride_row, c)] = TileType.PATH
    park.grid[park.to_index(right_ride_row, right_ride_col)] = TileType.RIDE

    stalls = [
        (mid_row,     mid_col + 8),
        (mid_row - 3, mid_col - 6),
        (mid_row + 3, mid_col + 3),
    ]
    for r, c in stalls:
        if 0 <= r < park.height and 0 <= c < park.width:
            if c > mid_col:
                for pc in range(mid_col + 1, c):
                    park.grid[park.to_index(r, pc)] = TileType.PATH
            else:
                for pc in range(c + 1, mid_col):
                    park.grid[park.to_index(r, pc)] = TileType.PATH
            park.grid[park.to_index(r, c)] = TileType.STALL

    toilets = [
        (park.height - 6, 3),
        (park.height - 8, park.width - 4),
    ]
    for r, c in toilets:
        if 0 <= r < park.height and 0 <= c < park.width:
            for pc in range(min(c, mid_col), max(c, mid_col) + 1):
                park.grid[park.to_index(r, pc)] = TileType.PATH
            park.grid[park.to_index(r, c)] = TileType.TOILET

    plaza_toilet_row = mid_row + 1
    plaza_toilet_col = mid_col - 2
    for rr in range(min(mid_row, plaza_toilet_row), max(mid_row, plaza_toilet_row) + 1):
        park.grid[park.to_index(rr, plaza_toilet_col)] = TileType.PATH
    park.grid[park.to_index(plaza_toilet_row, plaza_toilet_col)] = TileType.TOILET