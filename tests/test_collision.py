from models import Train
from models.event import EventType
from engine.event_queue import EventQueue
from engine.collision_monitor import CollisionMonitor


def test_collision_is_detected():

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

    # Simulate both trains being on the same track
    train_1.current_track = "TR1"
    train_2.current_track = "TR1"

    result = monitor.check_track_conflict(
        train_1,
        train_2
    )

    assert result is True

    assert train_1.state.value == "COLLISION_WARNING"
    assert train_2.state.value == "COLLISION_WARNING"

    event = event_queue.get()

    assert event.event_type == EventType.COLLISION_WARNING


def test_emergency_stop():

    event_queue = EventQueue()

    monitor = CollisionMonitor(
        event_queue
    )

    train = Train(
        "T1",
        "Station A",
        "Station B"
    )

    train.current_track = "TR1"

    monitor.emergency_stop(train)

    assert train.state.value == "EMERGENCY_STOP"

    event = event_queue.get()

    assert event.event_type == EventType.EMERGENCY_STOP