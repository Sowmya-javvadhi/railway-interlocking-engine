from models import (
    RailwayNetwork,
    Station,
    Track,
    Signal,
    Train,
    Route
)

from engine.event_queue import EventQueue
from engine.event_processor import EventProcessor
from engine.interlocking import InterlockingEngine
from engine.train_simulator import TrainSimulator
from engine.system_monitor import SystemMonitor


def create_network():

    network = RailwayNetwork()

    # =========================
    # STATIONS
    # =========================

    network.add_station(
        Station("S1", "Station A")
    )

    network.add_station(
        Station("S2", "Station B")
    )

    network.add_station(
        Station("S3", "Station C")
    )

    network.add_station(
        Station("S4", "Station D")
    )

    network.add_station(
        Station("S5", "Station E")
    )

    network.add_station(
        Station("S6", "Station F")
    )

    # =========================
    # TRACKS
    # =========================

    network.add_track(
        Track("TR1", "Station A", "Junction J1")
    )

    network.add_track(
        Track("TR2", "Junction J1", "Station B")
    )

    network.add_track(
        Track("TR3", "Junction J1", "Station C")
    )

    network.add_track(
        Track("TR4", "Station D", "Junction J1")
    )

    network.add_track(
        Track("TR5", "Junction J1", "Junction J2")
    )

    network.add_track(
        Track("TR6", "Junction J1", "Junction J2")
    )

    network.add_track(
        Track("TR7", "Junction J2", "Station E")
    )

    network.add_track(
        Track("TR8", "Junction J2", "Station F")
    )

    network.add_track(
        Track("TR9", "Station E", "Station F")
    )

    network.add_track(
        Track("TR10", "Station F", "Station E")
    )

    # =========================
    # SIGNALS
    # =========================

    for i in range(1, 11):

        network.add_signal(
            Signal(f"SIG{i}")
        )

    return network


def main():

    # =========================
    # CREATE NETWORK
    # =========================

    network = create_network()

    # =========================
    # EVENT SYSTEM
    # =========================

    event_queue = EventQueue()

    event_processor = EventProcessor(
        event_queue
    )

    event_processor.start()

    # =========================
    # INTERLOCKING ENGINE
    # =========================

    interlocking = InterlockingEngine(
        network,
        event_queue
    )

    # =========================
    # TRAIN SIMULATOR
    # =========================

    simulator = TrainSimulator(
        interlocking
    )

    # =========================
    # ROUTES
    # =========================

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

    route_3 = Route(
        "R3",
        "Station D",
        "Station B",
        ["TR4", "TR2"]
    )

    route_4 = Route(
        "R4",
        "Station D",
        "Station C",
        ["TR4", "TR3"]
    )

    route_5 = Route(
        "R5",
        "Station A",
        "Station E",
        ["TR1", "TR5", "TR7"]
    )

    route_6 = Route(
        "R6",
        "Station D",
        "Station F",
        ["TR4", "TR6", "TR8"]
    )

    route_7 = Route(
        "R7",
        "Station B",
        "Station E",
        ["TR2", "TR5", "TR7"]
    )

    route_8 = Route(
        "R8",
        "Station C",
        "Station F",
        ["TR3", "TR6", "TR8"]
    )

    route_9 = Route(
        "R9",
        "Station E",
        "Station F",
        ["TR9"]
    )

    route_10 = Route(
        "R10",
        "Station F",
        "Station E",
        ["TR10"]
    )

    # =========================
    # TRAINS
    # =========================

    train_1 = Train(
        "T1",
        "Station A",
        "Station B",
        speed=2
    )

    train_2 = Train(
        "T2",
        "Station A",
        "Station C",
        speed=2
    )

    train_3 = Train(
        "T3",
        "Station D",
        "Station B",
        speed=2
    )

    train_4 = Train(
        "T4",
        "Station D",
        "Station C",
        speed=2
    )

    train_5 = Train(
        "T5",
        "Station A",
        "Station E",
        speed=2
    )

    train_6 = Train(
        "T6",
        "Station D",
        "Station F",
        speed=2
    )

    train_7 = Train(
        "T7",
        "Station B",
        "Station E",
        speed=2
    )

    train_8 = Train(
        "T8",
        "Station C",
        "Station F",
        speed=2
    )

    train_9 = Train(
        "T9",
        "Station E",
        "Station F",
        speed=2
    )

    train_10 = Train(
        "T10",
        "Station F",
        "Station E",
        speed=2
    )

    # =========================
    # TRAIN + ROUTE MAPPING
    # =========================

    train_routes = [
        (train_1, route_1),
        (train_2, route_2),
        (train_3, route_3),
        (train_4, route_4),
        (train_5, route_5),
        (train_6, route_6),
        (train_7, route_7),
        (train_8, route_8),
        (train_9, route_9),
        (train_10, route_10)
    ]

    trains = [
        train_1,
        train_2,
        train_3,
        train_4,
        train_5,
        train_6,
        train_7,
        train_8,
        train_9,
        train_10
    ]

    # =========================
    # SYSTEM MONITOR
    # =========================

    monitor = SystemMonitor(
        network,
        interlocking,
        trains
    )

    # =========================
    # START SIMULATION
    # =========================

    print(
        "\n=========================================="
    )

    print(
        "   AUTOMATED RAILWAY INTERLOCKING SYSTEM"
    )

    print(
        "=========================================="
    )

    print(
        "\nNetwork initialized:"
    )

    print(
        f"Stations : {len(network.stations)}"
    )

    print(
        f"Tracks   : {len(network.tracks)}"
    )

    print(
        f"Signals  : {len(network.signals)}"
    )

    print(
        f"Trains   : {len(trains)}"
    )

    print(
        "\n===== Starting Railway Simulation ====="
    )

    # =========================
    # START ALL TRAINS
    # =========================

    for train, route in train_routes:

        simulator.start_train(
            train,
            route
        )

    # =========================
    # WAIT FOR ALL TRAINS
    # =========================

    for train in trains:

        simulator.wait_for_train(
            train
        )

    # =========================
    # FINAL SYSTEM STATUS
    # =========================

    monitor.display_status()

    # Wait until all queued events
    # have been processed.

    event_queue.join()

    # Stop event processor.

    event_processor.stop()

    # =========================
    # FINAL RESULTS
    # =========================

    print(
        "\n===== Simulation Complete ====="
    )

    for train in trains:

        print(
            f"{train.train_id}: "
            f"{train.state.value}"
        )

    print(
        "\n=========================================="
    )

    print(
        "       RAILWAY SYSTEM SHUTDOWN"
    )

    print(
        "=========================================="
    )


if __name__ == "__main__":

    main()