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


def test_stress_multiple_concurrent_trains():

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

    # Create 20 concurrent trains
    for i in range(20):

        if i % 2 == 0:

            train = Train(
                f"ST{i + 1}",
                "Station A",
                "Station B",
                speed=10
            )

            route = route_1

        else:

            train = Train(
                f"ST{i + 1}",
                "Station A",
                "Station C",
                speed=10
            )

            route = route_2

        trains.append(
            (train, route)
        )

    # Start all trains
    for train, route in trains:

        simulator.start_train(
            train,
            route
        )

    # Wait for every train
    for train, route in trains:

        assert train.thread is not None

        train.thread.join(
            timeout=10
        )

        assert not train.thread.is_alive(), (
            f"Train {train.train_id} "
            f"did not finish"
        )

    # Verify every train arrived
    for train, route in trains:

        assert train.state.value == "ARRIVED"

        assert train.current_track is None

    # Verify no track remains occupied
    for track in network.tracks.values():

        assert track.occupied_by is None
        assert track.reserved_by is None