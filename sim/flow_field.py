from dataclasses import dataclass, field
from .constants import PARK_WIDTH, PARK_HEIGHT, FLOW_FIELD_INFINITY
import heapq
from .tiles import TileType

EXIT_GOAL_TILES = {TileType.ENTRANCE}
GOAL_TILES = {TileType.RIDE, TileType.STALL, TileType.TOILET}
WALKABLE_TILES = {TileType.PATH, TileType.ENTRANCE, TileType.RIDE, TileType.STALL, TileType.TOILET}
NEIGHBOUR_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
GOAL_COSTS = {
    TileType.RIDE:   0,
    TileType.STALL:  1,
    TileType.TOILET: 1,
    TileType.ENTRANCE: 0
}
@dataclass
class FlowField:
    width: int = PARK_WIDTH
    height: int = PARK_HEIGHT
    directions: list = field(default_factory=lambda: [(0, 0)] * (PARK_WIDTH * PARK_HEIGHT))

    def to_index(self, row, col):
        return row * self.width + col

    def get_direction(self, row, col):
        return self.directions[self.to_index(row, col)]

    def is_within_bounds(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def recompute(self, grid):
        self._recompute_with_goals(grid, GOAL_TILES)

    def recompute_for_exit(self, grid):
        self._recompute_with_goals(grid, EXIT_GOAL_TILES)

    def _recompute_with_goals(self, grid, goals):
        cost = [FLOW_FIELD_INFINITY] * (self.width * self.height)
        directions = [(0, 0)] * (self.width * self.height)
        queue = []

        self._seed_goals(grid, cost, queue, goals)

        while queue:
            self._process_tile(queue, cost, directions, grid)

        self.directions = directions

    def _seed_goals(self, grid, cost, queue, goals):
        for row in range(self.height):
            for col in range(self.width):
                tile = grid[self.to_index(row, col)]
                if tile in goals:
                    goal_cost = GOAL_COSTS.get(tile, 0)
                    cost[self.to_index(row, col)] = goal_cost
                    heapq.heappush(queue, (goal_cost, row, col))

    def _process_tile(self, queue, cost, directions, grid):
        current_cost, row, col = heapq.heappop(queue)

        if self._is_stale(current_cost, row, col, cost):
            return

        for row_delta, col_delta in NEIGHBOUR_OFFSETS:
            neighbour_row = row + row_delta
            neighbour_col = col + col_delta

            if not self.is_within_bounds(neighbour_row, neighbour_col):
                continue

            if not self._is_walkable(neighbour_row, neighbour_col, grid):
                continue

            self._relax(neighbour_row, neighbour_col, row_delta, col_delta, current_cost, cost, directions, queue)

    def _is_stale(self, current_cost, row, col, cost):
        return current_cost > cost[self.to_index(row, col)]

    def _is_walkable(self, row, col, grid):
        return grid[self.to_index(row, col)] in WALKABLE_TILES

    def _relax(self, neighbour_row, neighbour_col, row_delta, col_delta, current_cost, cost, directions, queue):
        new_cost = current_cost + 1
        neighbour_index = self.to_index(neighbour_row, neighbour_col)

        if new_cost < cost[neighbour_index]:
            cost[neighbour_index] = new_cost
            directions[neighbour_index] = (-row_delta, -col_delta)
            heapq.heappush(queue, (new_cost, neighbour_row, neighbour_col))