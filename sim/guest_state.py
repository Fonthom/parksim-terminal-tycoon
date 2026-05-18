from enum import Enum

class GuestState(Enum):
    WANDERING = "wandering"
    HUNGRY = "hungry"
    QUEUING = "queuing"
    RIDING = "riding"
    EXITING = "exiting"
    LEFT = "left"