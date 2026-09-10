from threading import Lock

from models.network import RailwayNetwork
from models.route import Route
from models.event import Event, EventType

from engine.event_queue import EventQueue
from engine.signal_controller import SignalController


class InterlockingEngine:

    def __init__(
        self,
        network: RailwayNetwork,
        event_queue: EventQueue
    ):

        self.network = network
        self.event_queue = event_queue

        self.lock = Lock()

        self.active_routes: dict[str, str] = {}

        self.signal_controller = SignalController(
            event_queue
        )

    def request_route(
        self,
        train_id: str,
        route: Route
    ) -> bool:

        with self.lock:

            # Check every track before reserving anything
            for track_id in route.track_ids:

                track = self.network.get_track(
                    track_id
                )

                if track is None:

                    self._publish_rejection(
                        train_id,
                        route.route_id,
                        f"Track {track_id} does not exist"
                    )

                    return False

                if not track.is_available():

                    self._publish_rejection(
                        train_id,
                        route.route_id,
                        f"Track {track_id} is unavailable"
                    )

                    return False

            reserved_tracks = []

            # Reserve all tracks
            for track_id in route.track_ids:

                track = self.network.get_track(
                    track_id
                )

                if track.reserve(train_id):

                    reserved_tracks.append(
                        track_id
                    )

                else:

                    # Roll back previous reservations
                    for reserved_id in reserved_tracks:

                        reserved_track = (
                            self.network.get_track(
                                reserved_id
                            )
                        )

                        if reserved_track:
                            reserved_track.release(
                                train_id
                            )

                    self._publish_rejection(
                        train_id,
                        route.route_id,
                        "Route reservation failed"
                    )

                    return False

            # Store active route
            self.active_routes[
                route.route_id
            ] = train_id

            # Set associated signal to GREEN
            signal = self._get_signal_for_route(
                route
            )

            if signal:

                self.signal_controller.set_green(
                    signal,
                    train_id
                )

            self.event_queue.publish(
                Event(
                    event_type=EventType.ROUTE_GRANTED,
                    train_id=train_id,
                    resource_id=route.route_id,
                    message=(
                        f"Route {route.route_id} granted. "
                        f"Tracks reserved: "
                        f"{reserved_tracks}"
                    )
                )
            )

            return True

    def release_route(
        self,
        train_id: str,
        route: Route
    ) -> bool:

        with self.lock:

            owner = self.active_routes.get(
                route.route_id
            )

            if owner != train_id:
                return False

            # Release all reserved tracks
            for track_id in route.track_ids:

                track = self.network.get_track(
                    track_id
                )

                if track:

                    track.release(
                        train_id
                    )

            # Set associated signal to RED
            signal = self._get_signal_for_route(
                route
            )

            if signal:

                self.signal_controller.set_red(
                    signal,
                    train_id
                )

            del self.active_routes[
                route.route_id
            ]

            self.event_queue.publish(
                Event(
                    event_type=EventType.TRACK_RELEASED,
                    train_id=train_id,
                    resource_id=route.route_id,
                    message=(
                        f"Route {route.route_id} released"
                    )
                )
            )

            return True

    def _get_signal_for_route(
        self,
        route: Route
    ):

        # Convention:
        # R1 -> SIG1
        # R2 -> SIG2
        # R3 -> SIG3

        signal_id = (
            "SIG"
            + route.route_id.replace("R", "")
        )

        return self.network.get_signal(
            signal_id
        )

    def _publish_rejection(
        self,
        train_id: str,
        route_id: str,
        reason: str
    ):

        self.event_queue.publish(
            Event(
                event_type=EventType.ROUTE_REJECTED,
                train_id=train_id,
                resource_id=route_id,
                message=reason
            )
        )