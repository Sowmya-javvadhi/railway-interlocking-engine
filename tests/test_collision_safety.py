from models import Train, Track
from models.event import EventType

from engine.event_queue import EventQueue
from engine.collision_monitor import CollisionMonitor


def test_collision_triggers_emergency_stop():

    event_queue = EventQueue()

    monitor = CollisionMonitor(
        event_queue
    )

    train_1 = Train(
        "T1",
        "Station A",
        "Station B"
    )

    train_2 = Train(
        "T2",
        "Station C",
        "Station D"
    )

    # Simulate both trains entering the same track
    train_1.current_track = "TR1"
    train_2.current_track = "TR1"

    collision = monitor.check_track_conflict(
        train_1,
        train_2
    )

    assert collision is True

    # Both trains should receive collision warning
    assert train_1.state.value == "COLLISION_WARNING"
    assert train_2.state.value == "COLLISION_WARNING"

    # Emergency stop the affected train
    monitor.emergency_stop(train_1)

    assert train_1.state.value == "EMERGENCY_STOP"

    # Verify emergency-stop event
    events = []

    while not event_queue.empty():
        events.append(
            event_queue.get()
        )

    event_types = [
        event.event_type
        for event in events
    ]

    assert EventType.COLLISION_WARNING in event_types
    assert EventType.EMERGENCY_STOP in event_types