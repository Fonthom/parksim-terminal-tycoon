from sim.guest_needs import check_should_exit
from sim.guest_state import GuestState
from sim.guest import Guest
from sim.guest_needs import tick_needs
from sim.constants import HUNGER_RATE, BLADDER_RATE
from sim.constants import BLADDER_RATE_AFTER_EATING
from sim.guest_needs import check_bladder_accident
from sim.guest_needs import check_should_exit
from sim.constants import HAPPINESS_EXIT_THRESHOLD


def make_guest():
    return Guest(row=10, col=10, hunger=0.0, bladder=0.0, happiness=1.0, money=50.0)
 
def test_tick_needs_increases_hunger_and_bladder():
    g = make_guest()
    tick_needs(g)
    assert g.hunger  == HUNGER_RATE
    assert g.bladder == BLADDER_RATE
 
def test_tick_needs_uses_bladder_rate():
    g = make_guest()
    g.bladder_rate = BLADDER_RATE_AFTER_EATING
    tick_needs(g)
    assert g.bladder == BLADDER_RATE_AFTER_EATING
 
def test_check_bladder_accident_triggers_at_1():
    g = make_guest()
    g.bladder = 1.0
    check_bladder_accident(g)
    assert g.bladder   == 0.0
    assert g.happiness == 0.0
 
def test_check_bladder_accident_no_trigger_below_1():
    g = make_guest()
    g.bladder = 0.99
    check_bladder_accident(g)
    assert g.bladder   == 0.99
    assert g.happiness == 1.0
 
def test_check_should_exit_no_money():
    g = make_guest()
    g.money = 0.0
    result = check_should_exit(g)
    assert result is True
    assert g.state  == GuestState.EXITING
    assert g.target is None
 
def test_check_should_exit_low_happiness():
    g = make_guest()
    g.happiness = HAPPINESS_EXIT_THRESHOLD
    result = check_should_exit(g)
    assert result is True
    assert g.state == GuestState.EXITING
 
def test_check_should_exit_healthy_guest():
    g = make_guest()
    result = check_should_exit(g)
    assert result is False
    assert g.state == GuestState.WANDERING