from dataclasses import dataclass
from enum import Enum


class SignalState(Enum):
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"


@dataclass
class Signal:
    signal_id: str
    state: SignalState = SignalState.RED

    def set_state(self, state: SignalState):
        self.state = state

    def is_clear(self) -> bool:
        return self.state == SignalState.GREEN