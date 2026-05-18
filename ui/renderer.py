import curses
import time
from sim.park import Park
from sim.tiles import TileType
from sim.guest import GuestState
from sim.constants import PARK_WIDTH, PARK_HEIGHT, TICK_RATE
from ui.constants import HUD_WIDTH, HUD_COL_OFFSET
from ui.colors import init_colors, PAIR_HUD, PAIR_HUD_POS, PAIR_HUD_NEG
from ui.chars import TILE_CHARS, GUEST_CHARS

def _draw_map(stdscr, park):
    guest_positions = {
        (guest.row, guest.col): guest.state
        for guest in park.guests
    }
    for row in range(park.height):
        for col in range(park.width):
            if (row, col) in guest_positions:
                char, pair = GUEST_CHARS[guest_positions[(row, col)]]
            else:
                char, pair = TILE_CHARS[park.get_tile(row, col)]
            try:
                stdscr.addstr(row, col, char, curses.color_pair(pair))
            except curses.error:
                pass

def _draw_hud(stdscr, park):
    hud_col = PARK_WIDTH + HUD_COL_OFFSET
    hud  = curses.color_pair(PAIR_HUD)
    pos  = curses.color_pair(PAIR_HUD_POS)
    neg  = curses.color_pair(PAIR_HUD_NEG)
    hungry  = sum(1 for g in park.guests if g.state == GuestState.HUNGRY)
    exiting = sum(1 for g in park.guests if g.state == GuestState.EXITING)

    rows = [
        (1,  "PARKSIM",                        hud | curses.A_BOLD),
        (3,  "FINANCES",                        hud | curses.A_UNDERLINE),
        (4,  f"Cash:    ${park.finance.cash:.0f}", pos if park.finance.cash > 0 else neg),
        (5,  f"Income:  ${park.finance.income_per_tick:.1f}/tick", pos),
        (6,  f"Upkeep:  ${park.finance.upkeep_per_tick:.1f}/tick", neg),
        (8,  "GUESTS",                          hud | curses.A_UNDERLINE),
        (9,  f"Total:   {len(park.guests)}",    pos),
        (10, f"Hungry:  {hungry}",              neg if hungry  > 0 else pos),
        (11, f"Exiting: {exiting}",             neg if exiting > 0 else pos),
        (13, "CONTROLS",                        hud | curses.A_UNDERLINE),
        (14, "[p] path",                        hud),
        (15, "[r] ride",                        hud),
        (16, "[s] stall",                       hud),
        (17, "[x] delete",                      hud),
        (18, "[space] pause",                   hud),
        (19, "[q] quit",                        hud),
    ]

    for row, text, style in rows:
        try:
            stdscr.addstr(row, hud_col, text, style)
        except curses.error:
            pass

def _draw_cursor(stdscr, park, cursor_row, cursor_col):
    char, pair = TILE_CHARS[park.get_tile(cursor_row, cursor_col)]
    try:
        stdscr.addstr(cursor_row, cursor_col, char, curses.color_pair(pair) | curses.A_REVERSE)
    except curses.error:
        pass

def _handle_input(key, park, paused, place_mode, cursor_row, cursor_col):
    if key == ord('q'):
        return None, paused, place_mode, cursor_row, cursor_col
    elif key == ord(' '):
        paused = not paused
    elif key == ord('p'):
        place_mode = TileType.PATH
    elif key == ord('r'):
        place_mode = TileType.RIDE
    elif key == ord('s'):
        place_mode = TileType.STALL
    elif key == ord('x'):
        place_mode = TileType.GRASS
    elif key == curses.KEY_UP:
        cursor_row = max(0, cursor_row - 1)
    elif key == curses.KEY_DOWN:
        cursor_row = min(PARK_HEIGHT - 1, cursor_row + 1)
    elif key == curses.KEY_LEFT:
        cursor_col = max(0, cursor_col - 1)
    elif key == curses.KEY_RIGHT:
        cursor_col = min(PARK_WIDTH - 1, cursor_col + 1)
    elif key == ord('\n'):
        if park.get_tile(cursor_row, cursor_col) != TileType.ENTRANCE:
            park.set_tile(cursor_row, cursor_col, place_mode)
    return park, paused, place_mode, cursor_row, cursor_col

def _run(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    park = Park()
    paused = False
    place_mode = TileType.PATH
    cursor_row = PARK_HEIGHT // 2
    cursor_col = PARK_WIDTH // 2

    while True:
        key = stdscr.getch()
        result = _handle_input(key, park, paused, place_mode, cursor_row, cursor_col)

        if result[0] is None:
            break

        park, paused, place_mode, cursor_row, cursor_col = result

        if not paused:
            park.tick()

        if park.guests:
            g = park.guests[0]
            stdscr.addstr(22, PARK_WIDTH + HUD_COL_OFFSET,
                f"state:{g.state} pos:({g.row},{g.col})")
            stdscr.addstr(23, PARK_WIDTH + HUD_COL_OFFSET,
                f"exit_dir:{park.exit_field.get_direction(g.row, g.col)}")

        stdscr.erase()
        _draw_map(stdscr, park)
        _draw_hud(stdscr, park)
        _draw_cursor(stdscr, park, cursor_row, cursor_col)
        stdscr.refresh()
        time.sleep(TICK_RATE)

def start():
    curses.wrapper(_run)