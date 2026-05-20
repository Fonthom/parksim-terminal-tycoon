import curses
import time
from sim.park import Park
from sim.tiles import TileType
from sim.guest_state import GuestState
from sim.constants import (
    PARK_WIDTH, PARK_HEIGHT, TICK_RATE,
    PRICE_STEP, PRICE_MIN, PRICE_MAX
)
from ui.colors import init_colors, PAIR_HUD, PAIR_HUD_POS, PAIR_HUD_NEG
from ui.chars import TILE_CHARS, GUEST_CHARS
from ui.constants import HUD_WIDTH, HUD_COL_OFFSET

PRICE_FIELDS = ["entrance_fee", "ride_price", "stall_price", "toilet_price"]
PRICE_LABELS = ["Entrance", "Ride", "Stall", "Toilet"]

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

def _draw_hud(stdscr, park, mode, place_mode, price_cursor):
    hud_col = PARK_WIDTH + HUD_COL_OFFSET
    hud  = curses.color_pair(PAIR_HUD)
    pos  = curses.color_pair(PAIR_HUD_POS)
    neg  = curses.color_pair(PAIR_HUD_NEG)
    dim  = curses.color_pair(PAIR_HUD) | curses.A_DIM
    hungry  = sum(1 for g in park.guests if g.state == GuestState.HUNGRY)
    exiting = sum(1 for g in park.guests if g.state == GuestState.EXITING)

    # mode status bar
    if mode == "build":
        mode_text  = f" BUILD: {place_mode.value.upper()}".ljust(HUD_WIDTH)
        mode_style = curses.color_pair(PAIR_HUD_POS) | curses.A_BOLD | curses.A_REVERSE
    elif mode == "edit":
        mode_text  = " EDIT PRICES".ljust(HUD_WIDTH)
        mode_style = curses.color_pair(PAIR_HUD_NEG) | curses.A_BOLD | curses.A_REVERSE
    else:
        mode_text  = " WATCH MODE".ljust(HUD_WIDTH)
        mode_style = curses.color_pair(PAIR_HUD) | curses.A_REVERSE

    try:
        stdscr.addstr(0, hud_col, mode_text, mode_style)
    except curses.error:
        pass

    rows = [
        (2,  "PARKSIM",                                              hud | curses.A_BOLD),
        (4,  "FINANCES",                                             hud | curses.A_UNDERLINE),
        (5,  f"Cash:       ${park.finance.cash:.0f}",                pos if park.finance.cash > 0 else neg),
        (6,  f"Pending:    ${park.finance.accumulated_income:.0f}",  pos),
        (7,  f"Settlement: {park.finance.seconds_until_next_settlement()}s", hud),
        (9,  "GUESTS",                                               hud | curses.A_UNDERLINE),
        (10, f"Total:   {len(park.guests)}",                         pos),
        (11, f"Hungry:  {hungry}",                                   neg if hungry  > 0 else pos),
        (12, f"Exiting: {exiting}",                                  neg if exiting > 0 else pos),
    ]

    for row, text, style in rows:
        try:
            stdscr.addstr(row, hud_col, text, style)
        except curses.error:
            pass

    _draw_prices(stdscr, park, mode, price_cursor, hud_col, hud, pos)
    _draw_controls(stdscr, mode, place_mode, hud_col, hud, dim)

def _draw_prices(stdscr, park, mode, price_cursor, hud_col, hud, pos):
    try:
        stdscr.addstr(14, hud_col, "PRICES", hud | curses.A_UNDERLINE)
    except curses.error:
        pass

    for i, (field_name, label) in enumerate(zip(PRICE_FIELDS, PRICE_LABELS)):
        price = getattr(park.finance, field_name)
        text  = f"{label+':':<10} ${price:.0f}"
        if mode == "edit" and i == price_cursor:
            style = curses.color_pair(PAIR_HUD_POS) | curses.A_REVERSE
        else:
            style = pos
        try:
            stdscr.addstr(15 + i, hud_col, text, style)
        except curses.error:
            pass

def _draw_controls(stdscr, mode, place_mode, hud_col, hud, dim):
    build_active = mode == "build"
    edit_active  = mode == "edit"

    controls = [
        (20, "CONTROLS",        hud | curses.A_UNDERLINE),
        (21, "[b] build mode",  hud),
        (22, "[e] edit prices", hud),
        (23, "[p] path",        hud if build_active else dim),
        (24, "[r] ride",        hud if build_active else dim),
        (25, "[s] stall",       hud if build_active else dim),
        (26, "[t] toilet",      hud if build_active else dim),
        (27, "[x] delete",      hud if build_active else dim),
        (28, "[enter] place",   hud if build_active else dim),
        (29, "[↑/↓] select",    hud if edit_active  else dim),
        (30, "[+/-] adjust",    hud if edit_active  else dim),
        (31, "[space] pause",   hud),
        (32, "[q] quit",        hud),
    ]

    for row, text, style in controls:
        try:
            stdscr.addstr(row, hud_col, text, style)
        except curses.error:
            pass

def _draw_cursor(stdscr, park, cursor_row, cursor_col, mode):
    char, pair = TILE_CHARS[park.get_tile(cursor_row, cursor_col)]
    style = curses.color_pair(pair) | curses.A_REVERSE
    if mode == "build":
        style = style | curses.A_BOLD
    try:
        stdscr.addstr(cursor_row, cursor_col, char, style)
    except curses.error:
        pass

def _handle_input(key, park, paused, mode, place_mode, cursor_row, cursor_col, price_cursor):
    if key == ord('q'):
        return None, paused, mode, place_mode, cursor_row, cursor_col, price_cursor
    elif key == ord(' '):
        paused = not paused
    elif key == ord('b'):
        mode = "watch" if mode == "build" else "build"
    elif key == ord('e'):
        mode = "watch" if mode == "edit" else "edit"

    elif mode == "edit":
        if key == curses.KEY_UP:
            price_cursor = max(0, price_cursor - 1)
        elif key == curses.KEY_DOWN:
            price_cursor = min(len(PRICE_FIELDS) - 1, price_cursor + 1)
        elif key in (ord('+'), ord('=')):
            field_name = PRICE_FIELDS[price_cursor]
            current    = getattr(park.finance, field_name)
            setattr(park.finance, field_name, min(PRICE_MAX, current + PRICE_STEP))
        elif key == ord('-'):
            field_name = PRICE_FIELDS[price_cursor]
            current    = getattr(park.finance, field_name)
            setattr(park.finance, field_name, max(PRICE_MIN, current - PRICE_STEP))

    elif mode == "build":
        if key == ord('p'):
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
            if place_mode == TileType.GRASS:
                park.demolish_tile(cursor_row, cursor_col)
            else:
                park.place_tile(cursor_row, cursor_col, place_mode)

    else:  # watch mode
        if key == curses.KEY_UP:
            cursor_row = max(0, cursor_row - 1)
        elif key == curses.KEY_DOWN:
            cursor_row = min(PARK_HEIGHT - 1, cursor_row + 1)
        elif key == curses.KEY_LEFT:
            cursor_col = max(0, cursor_col - 1)
        elif key == curses.KEY_RIGHT:
            cursor_col = min(PARK_WIDTH - 1, cursor_col + 1)

    return park, paused, mode, place_mode, cursor_row, cursor_col, price_cursor

def _run(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    park         = Park()
    paused       = False
    mode         = "watch"
    place_mode   = TileType.PATH
    cursor_row   = PARK_HEIGHT // 2
    cursor_col   = PARK_WIDTH // 2
    price_cursor = 0

    while True:
        key    = stdscr.getch()
        result = _handle_input(
            key, park, paused, mode,
            place_mode, cursor_row, cursor_col, price_cursor
        )

        if result[0] is None:
            break

        park, paused, mode, place_mode, cursor_row, cursor_col, price_cursor = result

        if not paused:
            park.tick()

        stdscr.erase()
        _draw_map(stdscr, park)
        _draw_hud(stdscr, park, mode, place_mode, price_cursor)
        _draw_cursor(stdscr, park, cursor_row, cursor_col, mode)
        stdscr.refresh()
        time.sleep(TICK_RATE)

def start():
    curses.wrapper(_run)