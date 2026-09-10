from models import (
    RailwayNetwork,
    Station,
    Track,
    Route,
    Event
)

from engine.event_queue import EventQueue
from engine.interlocking import InterlockingEngine


def create_test_network():

    network = RailwayNetwork()

    network.add_station(
        Station("S1", "Station A")
    )

    network.add_station(
        Station("S2", "Station B")
    )

    network.add_station(
        Station("S3", "Station C")
    )

    network.add_track(
        Track(
            "TR1",
            "Station A",
            "Junction J1"
        )
    )

    network.add_track(
        Track(
            "TR2",
            "Junction J1",
            "Station B"
        )
    )

    network.add_track(
        Track(
            "TR3",
            "Junction J1",
            "Station C"
        )
    )

    return network


def test_route_can_be_granted():

    network = create_test_network()

    event_queue = EventQueue()

    engine = InterlockingEngine(
        network,
        event_queue
    )

    route = Route(
        "R1",
        "Station A",
        "Station B",
        ["TR1", "TR2"]
    )

    result = engine.request_route(
        "T1",
        route
    )

    assert result is True

    assert network.tracks["TR1"].reserved_by == "T1"
    assert network.tracks["TR2"].reserved_by == "T1"


def test_conflicting_route_is_rejected():

    network = create_test_network()

    event_queue = EventQueue()

    engine = InterlockingEngine(
        network,
        event_queue
    )

    route_1 = Route(
        "R1",
        "Station A",
        "Station B",
        ["TR1", "TR2"]
    )

    route_2 = Route(
        "R2",
        "Station A",
        "Station C",
        ["TR1", "TR3"]
    )

    first_result = engine.request_route(
        "T1",
        route_1
    )

    second_result = engine.request_route(
        "T2",
        route_2
    )

    assert first_result is True
    assert second_result is False


def test_route_can_be_released():

    network = create_test_network()

    event_queue = EventQueue()

    engine = InterlockingEngine(
        network,
        event_queue
    )

    route = Route(
        "R1",
        "Station A",
        "Station B",
        ["TR1", "TR2"]
    )

    assert engine.request_route(
        "T1",
        route
    ) is True

    assert engine.release_route(
        "T1",
        route
    ) is True

    assert network.tracks["TR1"].reserved_by is None
    assert network.tracks["TR2"].reserved_by is None