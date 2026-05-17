from enum import Enum

class GuestState(Enum):
    WANDERING,
    HUNGRY,
    QUEUING,
    RIDING,
    LEAVING,