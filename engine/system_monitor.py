from models.train import Train
from models.network import RailwayNetwork
from engine.interlocking import InterlockingEngine


class SystemMonitor:

    def __init__(
        self,
        network: RailwayNetwork,
        interlocking: InterlockingEngine,
        trains: list[Train]
    ):

        self.network = network
        self.interlocking = interlocking
        self.trains = trains

    def display_status(self):

        print("\n===== SYSTEM STATUS =====")

        print("\nTrains:")

        for train in self.trains:

            track = train.current_track or "NONE"

            print(
                f"  {train.train_id} | "
                f"State: {train.state.value} | "
                f"Track: {track}"
            )

        print("\nTracks:")

        for track in self.network.tracks.values():

            if track.occupied_by:
                status = f"OCCUPIED BY {track.occupied_by}"

            elif track.reserved_by:
                status = f"RESERVED BY {track.reserved_by}"

            else:
                status = "FREE"

            print(
                f"  {track.track_id}: {status}"
            )

        print("\nSignals:")

        for signal in self.network.signals.values():

            print(
                f"  {signal.signal_id}: "
                f"{signal.state.value}"
            )

        print("\nActive Routes:")

        if not self.interlocking.active_routes:

            print("  None")

        else:

            for route_id, train_id in (
                self.interlocking.active_routes.items()
            ):

                print(
                    f"  {route_id} → {train_id}"
                )

        print("\n=========================\n")