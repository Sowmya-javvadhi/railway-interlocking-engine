from dataclasses import dataclass, field
from enum import Enum
from threading import Thread


class TrainState(Enum):
    CREATED = "CREATED"
    WAITING = "WAITING"
    ROUTE_REQUESTED = "ROUTE_REQUESTED"
    ROUTE_GRANTED = "ROUTE_GRANTED"
    MOVING = "MOVING"
    WAITING_FOR_TRACK = "WAITING_FOR_TRACK"
    COLLISION_WARNING = "COLLISION_WARNING"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    ARRIVED = "ARRIVED"


@dataclass
class Train:
    train_id: str
    source: str
    destination: str
    speed: float = 1.0

    state: TrainState = TrainState.CREATED
    current_track: str | None = None

    route: list[str] = field(default_factory=list)

    thread: Thread | None = field(default=None, repr=False)

    def set_state(self, state: TrainState):
        self.state = state

    def assign_route(self, route: list[str]):
        self.route = route

    def __str__(self):
        return (
            f"Train({self.train_id}, "
            f"{self.source} -> {self.destination}, "
            f"state={self.state.value})"
        )