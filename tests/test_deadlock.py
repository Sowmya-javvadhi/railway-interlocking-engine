import threading
import time

from models import (
    RailwayNetwork,
    Station,
    Track,
    Train,
    Route
)

from engine.event_queue import EventQueue
from engine.interlocking import InterlockingEngine
from engine.train_simulator import TrainSimulator


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


def test_trains_do_not_deadlock():

    network = create_test_network()

    event_queue = EventQueue()

    interlocking = InterlockingEngine(
        network,
        event_queue
    )

    simulator = TrainSimulator(
        interlocking
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

    trains = []

    # Create several competing trains
    for i in range(6):

        if i % 2 == 0:

            train = Train(
                f"DL{i + 1}",
                "Station A",
                "Station B",
                speed=10
            )

            route = route_1

        else:

            train = Train(
                f"DL{i + 1}",
                "Station A",
                "Station C",
                speed=10
            )

            route = route_2

        trains.append((train, route))

    # Start all trains concurrently
    for train, route in trains:

        simulator.start_train(
            train,
            route
        )

    # Wait for every train with a timeout
    for train, route in trains:

        assert train.thread is not None

        train.thread.join(timeout=10)

        # If the thread is still alive, it is potentially deadlocked
        assert not train.thread.is_alive(), (
            f"Potential deadlock detected: "
            f"{train.train_id} did not finish"
        )

    # Every train should eventually arrive
    for train, route in trains:

        assert train.state.value == "ARRIVED"

        assert train.current_track is None

    # All resources should be released
    for track in network.tracks.values():

        assert track.occupied_by is None
        assert track.reserved_by is None