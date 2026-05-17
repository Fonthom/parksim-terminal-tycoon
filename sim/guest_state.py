from enum import Enum, auto

class GuestState(Enum):
    WANDERING = "wandering"
    HUNGRY = "hungry"
    QUEUING = "queuing"
    RIDING = "riding"
    LEAVING = "leaving"