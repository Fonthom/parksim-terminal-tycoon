from sim.guest import Guest
from sim.park import Park
from sim.guest_state import GuestState
from sim.constants import PARK_WIDTH,HUNGER_THRESHOLD, PARK_HEIGHT, BLADDER_RATE, BLADDER_THRESHOLD


def test_guest_constructs_with_defaults():
    g = Guest()
    assert g.row          == PARK_HEIGHT - 2
    assert g.col          == PARK_WIDTH // 2
    assert g.state        == GuestState.WANDERING
    assert g.happiness    == 1.0
    assert g.bladder_rate == BLADDER_RATE
    assert 0.0 <= g.hunger  <= 0.3
    assert 0.0 <= g.bladder <= 0.2
    assert 20.0 <= g.money  <= 80.0
 
def test_guest_switches_to_hungry():
    park  = Park()
    guest = Guest(row=park.height - 2, col=park.width // 2, hunger=HUNGER_THRESHOLD - 0.001)
    guest.update(park)
    assert guest.state == GuestState.HUNGRY
 
def test_guest_switches_to_need_toilet():
    park  = Park()
    guest = Guest(row=park.height - 2, col=park.width // 2, bladder=BLADDER_THRESHOLD - 0.001)
    guest.update(park)
    assert guest.state == GuestState.NEED_TOILET
 
def test_guest_switches_to_exiting_when_broke():
    park  = Park()
    guest = Guest(row=park.height - 2, col=park.width // 2, money=0.0)
    guest.update(park)
    assert guest.state == GuestState.EXITING
 
def test_guest_bladder_accident_zeroes_happiness():
    park  = Park()
    guest = Guest(row=park.height - 2, col=park.width // 2, bladder=1.0)
    guest.update(park)
    assert guest.happiness == 0.0
    assert guest.bladder   == 0.0
 
def test_guest_update_does_not_crash():
    park  = Park()
    guest = Guest(row=park.height - 2, col=park.width // 2)
    for _ in range(50):
        guest.update(park)