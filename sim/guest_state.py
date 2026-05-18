from enum import Enum

class GuestState(Enum):
    WANDERING = "wandering"
    HUNGRY = "hungry"
    NEED_TOILET = "need_toilet"
    QUEUING = "queuing"
    RIDING = "riding"
    EXITING = "exiting"
    LEFT = "left"