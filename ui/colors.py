import curses

PAIR_GRASS    = 1
PAIR_PATH     = 2
PAIR_RIDE     = 3
PAIR_STALL    = 4
PAIR_TOILET   = 5
PAIR_ENTRANCE = 6
PAIR_GUEST    = 7
PAIR_HUNGRY   = 8
PAIR_EXITING  = 9
PAIR_HUD      = 10
PAIR_HUD_POS  = 11
PAIR_HUD_NEG  = 12

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(PAIR_GRASS,    curses.COLOR_GREEN,  -1)
    curses.init_pair(PAIR_PATH,     curses.COLOR_WHITE,  -1)
    curses.init_pair(PAIR_RIDE,     curses.COLOR_CYAN,   -1)
    curses.init_pair(PAIR_STALL,    curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_TOILET,   curses.COLOR_RED,    -1)
    curses.init_pair(PAIR_ENTRANCE, curses.COLOR_WHITE,  -1)
    curses.init_pair(PAIR_GUEST,    curses.COLOR_WHITE,  -1)
    curses.init_pair(PAIR_HUNGRY,   curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_EXITING,  curses.COLOR_WHITE,  -1)
    curses.init_pair(PAIR_HUD,      curses.COLOR_WHITE,  -1)
    curses.init_pair(PAIR_HUD_POS,  curses.COLOR_GREEN,  -1)
    curses.init_pair(PAIR_HUD_NEG,  curses.COLOR_RED,    -1)