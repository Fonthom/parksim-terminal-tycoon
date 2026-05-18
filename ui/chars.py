import curses
from sim.tiles import TileType
from sim.guest_state import GuestState
from ui.colors import (
    PAIR_GRASS, PAIR_PATH, PAIR_RIDE, PAIR_STALL,
    PAIR_TOILET, PAIR_ENTRANCE, PAIR_GUEST,
    PAIR_HUNGRY, PAIR_EXITING
)

TILE_CHARS = {
    TileType.GRASS:    ('·', PAIR_GRASS),
    TileType.PATH:     ('░', PAIR_PATH),
    TileType.RIDE:     ('R', PAIR_RIDE),
    TileType.STALL:    ('S', PAIR_STALL),
    TileType.TOILET:   ('T', PAIR_TOILET),
    TileType.ENTRANCE: ('E', PAIR_ENTRANCE),
}

GUEST_CHARS = {
    GuestState.WANDERING: ('@', PAIR_GUEST),
    GuestState.HUNGRY:    ('!', PAIR_HUNGRY),
    GuestState.EXITING:   ('~', PAIR_EXITING),
    GuestState.LEFT:      (' ', PAIR_GRASS),
}