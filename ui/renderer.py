import curses
import time
from sim.park import Park
from sim.tiles import TileType
from sim.guest_state import GuestState
from sim.constants import PARK_WIDTH, PARK_HEIGHT, TICK_RATE
from ui.colors import init_colors, PAIR_HUD, PAIR_HUD_POS, PAIR_HUD_NEG
from ui.chars import TILE_CHARS, GUEST_CHARS
from ui.constants import HUD_WIDTH, HUD_COL_OFFSET

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

def _draw_hud(stdscr, park, build_mode, place_mode):
    hud_col = PARK_WIDTH + HUD_COL_OFFSET
    hud  = curses.color_pair(PAIR_HUD)
    pos  = curses.color_pair(PAIR_HUD_POS)
    neg  = curses.color_pair(PAIR_HUD_NEG)
    dim  = curses.color_pair(PAIR_HUD) | curses.A_DIM
    hungry  = sum(1 for g in park.guests if g.state == GuestState.HUNGRY)
    exiting = sum(1 for g in park.guests if g.state == GuestState.EXITING)

    # build mode status bar
    if build_mode:
        mode_text = f" BUILD: {place_mode.value.upper()}".ljust(HUD_WIDTH)
        mode_style = curses.color_pair(PAIR_HUD_POS) | curses.A_BOLD | curses.A_REVERSE
    else:
        mode_text = " WATCH MODE".ljust(HUD_WIDTH)
        mode_style = curses.color_pair(PAIR_HUD) | curses.A_REVERSE

    try:
        stdscr.addstr(0, hud_col, mode_text, mode_style)
    except curses.error:
        pass

    rows = [
        (2,  "PARKSIM",                           hud | curses.A_BOLD),
        (4,  "FINANCES",                                      hud | curses.A_UNDERLINE),
        (5,  f"Cash:       ${park.finance.cash:.0f}",         pos if park.finance.cash > 0 else neg),
        (6,  f"Pending:    ${park.finance.accumulated_income:.0f}", pos),
        (7,  f"Settlement: {park.finance.seconds_until_next_settlement()}s", hud),
        (9,  "GUESTS",                             hud | curses.A_UNDERLINE),
        (10, f"Total:   {len(park.guests)}",       pos),
        (11, f"Hungry:  {hungry}",                 neg if hungry  > 0 else pos),
        (12, f"Exiting: {exiting}",                neg if exiting > 0 else pos),
        (14, "CONTROLS",                           hud | curses.A_UNDERLINE),
        (15, "[b] toggle build",                   hud),
        (16, "[p] path",                           hud if build_mode else dim),
        (17, "[r] ride",                           hud if build_mode else dim),
        (18, "[s] stall",                          hud if build_mode else dim),
        (19, "[t] toilet",                         hud if build_mode else dim),
        (20, "[x] delete",                         hud if build_mode else dim),
        (21, "[enter] place",                      hud if build_mode else dim),
        (22, "[space] pause",                      hud),
        (23, "[q] quit",                           hud),
    ]

    for row, text, style in rows:
        try:
            stdscr.addstr(row, hud_col, text, style)
        except curses.error:
            pass

def _draw_cursor(stdscr, park, cursor_row, cursor_col, build_mode):
    char, pair = TILE_CHARS[park.get_tile(cursor_row, cursor_col)]
    style = curses.color_pair(pair) | curses.A_REVERSE
    if build_mode:
        style = style | curses.A_BOLD
    try:
        stdscr.addstr(cursor_row, cursor_col, char, style)
    except curses.error:
        pass

def _handle_input(key, park, paused, build_mode, place_mode, cursor_row, cursor_col):
    if key == ord('q'):
        return None, paused, build_mode, place_mode, cursor_row, cursor_col
    elif key == ord(' '):
        paused = not paused
    elif key == ord('b'):
        build_mode = not build_mode
    elif key == ord('p'):
        place_mode = TileType.PATH
    elif key == ord('r'):
        place_mode = TileType.RIDE
    elif key == ord('s'):
        place_mode = TileType.STALL
    elif key == ord('t'):
        place_mode = TileType.TOILET
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
    elif key in (curses.KEY_ENTER, 10, 13):
        if build_mode:
            if place_mode == TileType.GRASS:
                park.demolish_tile(cursor_row, cursor_col)
            else:
                park.place_tile(cursor_row, cursor_col, place_mode)
    return park, paused, build_mode, place_mode, cursor_row, cursor_col

def _run(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    park = Park()
    paused = False
    build_mode = False
    place_mode = TileType.PATH
    cursor_row = PARK_HEIGHT // 2
    cursor_col = PARK_WIDTH // 2

    while True:
        key = stdscr.getch()
        result = _handle_input(key, park, paused, build_mode, place_mode, cursor_row, cursor_col)

        if result[0] is None:
            break

        park, paused, build_mode, place_mode, cursor_row, cursor_col = result

        if not paused:
            park.tick()

        stdscr.erase()
        _draw_map(stdscr, park)
        _draw_hud(stdscr, park, build_mode, place_mode)
        _draw_cursor(stdscr, park, cursor_row, cursor_col, build_mode)
        stdscr.refresh()
        time.sleep(TICK_RATE)

def start():
    curses.wrapper(_run)