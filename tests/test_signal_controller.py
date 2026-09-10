from models import Signal, SignalState

from models.event import EventType

from engine.event_queue import EventQueue
from engine.signal_controller import SignalController


def test_signal_changes_to_green():

    event_queue = EventQueue()

    controller = SignalController(
        event_queue
    )

    signal = Signal("SIG1")

    controller.set_green(
        signal,
        "T1"
    )

    assert signal.state == SignalState.GREEN

    event = event_queue.get()

    assert event.event_type == EventType.SIGNAL_CHANGED
    assert event.train_id == "T1"
    assert event.resource_id == "SIG1"


def test_signal_changes_to_red():

    event_queue = EventQueue()

    controller = SignalController(
        event_queue
    )

    signal = Signal("SIG1")

    signal.set_state(
        SignalState.GREEN
    )

    controller.set_red(
        signal,
        "T1"
    )

    assert signal.state == SignalState.RED

    event = event_queue.get()

    assert event.event_type == EventType.SIGNAL_CHANGED
    assert event.train_id == "T1"
    assert event.resource_id == "SIG1"