from dataclasses import dataclass, field


@dataclass
class Route:
    route_id: str
    source: str
    destination: str
    track_ids: list[str] = field(default_factory=list)

    def contains_track(self, track_id: str) -> bool:
        return track_id in self.track_ids

    def conflicts_with(self, other: "Route") -> bool:
        return any(
            track_id in other.track_ids
            for track_id in self.track_ids
        )

    def __str__(self):
        tracks = " -> ".join(self.track_ids)

        return (
            f"Route({self.route_id}: "
            f"{self.source} -> {self.destination}, "
            f"tracks=[{tracks}])"
        )