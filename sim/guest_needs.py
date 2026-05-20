from .guest_state import GuestState
from .constants import (
    HUNGER_RATE, BLADDER_THRESHOLD,
    HAPPINESS_EXIT_THRESHOLD
)

def tick_needs(guest):
    guest.hunger += HUNGER_RATE
    guest.bladder += guest.bladder_rate

def check_bladder_accident(guest):
    if guest.bladder >= 1.0:
        guest.bladder = 0.0
        guest.happiness = 0.0

def check_should_exit(guest) -> bool:
    if guest.money <= 0 or guest.happiness <= HAPPINESS_EXIT_THRESHOLD:
        guest.state = GuestState.EXITING
        guest.target = None
        return True
    return False