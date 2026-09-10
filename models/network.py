from dataclasses import dataclass, field

from .station import Station
from .track import Track
from .signal import Signal


@dataclass
class RailwayNetwork:
    stations: dict[str, Station] = field(default_factory=dict)
    tracks: dict[str, Track] = field(default_factory=dict)
    signals: dict[str, Signal] = field(default_factory=dict)

    def add_station(self, station: Station):
        self.stations[station.station_id] = station

    def add_track(self, track: Track):
        self.tracks[track.track_id] = track

    def add_signal(self, signal: Signal):
        self.signals[signal.signal_id] = signal

    def get_station(self, station_id: str) -> Station | None:
        return self.stations.get(station_id)

    def get_track(self, track_id: str) -> Track | None:
        return self.tracks.get(track_id)

    def get_signal(self, signal_id: str) -> Signal | None:
        return self.signals.get(signal_id)

    def display_network(self):
        print("\n===== Railway Network =====")

        print("\nStations:")
        for station in self.stations.values():
            print(f"  {station.station_id}: {station.name}")

        print("\nTracks:")
        for track in self.tracks.values():
            print(
                f"  {track.track_id}: "
                f"{track.source} -> {track.destination}"
            )

        print("\nSignals:")
        for signal in self.signals.values():
            print(
                f"  {signal.signal_id}: "
                f"{signal.state.value}"
            )