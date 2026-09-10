from models.signal import SignalState
from models.event import Event, EventType

from engine.event_queue import EventQueue


class SignalController:

    def __init__(self, event_queue: EventQueue):

        self.event_queue = event_queue

    def set_green(
        self,
        signal,
        train_id: str
    ):

        signal.set_state(
            SignalState.GREEN
        )

        self.event_queue.publish(
            Event(
                event_type=EventType.SIGNAL_CHANGED,
                train_id=train_id,
                resource_id=signal.signal_id,
                message=(
                    f"Signal {signal.signal_id} "
                    f"changed to GREEN"
                )
            )
        )

    def set_red(
        self,
        signal,
        train_id: str
    ):

        signal.set_state(
            SignalState.RED
        )

        self.event_queue.publish(
            Event(
                event_type=EventType.SIGNAL_CHANGED,
                train_id=train_id,
                resource_id=signal.signal_id,
                message=(
                    f"Signal {signal.signal_id} "
                    f"changed to RED"
                )
            )
        )