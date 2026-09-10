import time
from threading import Thread

from models.train import Train, TrainState
from models.route import Route
from models.event import Event, EventType

from engine.interlocking import InterlockingEngine
from engine.collision_monitor import CollisionMonitor

from utils.logger import get_logger


class TrainSimulator:

    def __init__(self, interlocking: InterlockingEngine):

        self.interlocking = interlocking

        self.collision_monitor = CollisionMonitor(
            interlocking.event_queue
        )

        self.active_trains: list[Train] = []

        self.logger = get_logger("train_simulator")

    def run_train(
        self,
        train: Train,
        route: Route
    ):

        print(f"\n{train.train_id} started.")

        self.logger.info(
            f"Train {train.train_id} started"
        )

        self.event_queue_publish(
            EventType.TRAIN_STARTED,
            train.train_id,
            message=f"{train.train_id} started"
        )

        self.active_trains.append(train)

        train.set_state(
            TrainState.ROUTE_REQUESTED
        )

        self.event_queue_publish(
            EventType.ROUTE_REQUESTED,
            train.train_id,
            route.route_id,
            f"Route {route.route_id} requested"
        )

        # Request route until it is granted
        while True:

            print(
                f"{train.train_id} requesting route "
                f"{route.route_id}..."
            )

            granted = self.interlocking.request_route(
                train.train_id,
                route
            )

            if granted:
                break

            train.set_state(
                TrainState.WAITING_FOR_TRACK
            )

            print(
                f"{train.train_id}: Route unavailable. "
                f"Waiting before retry..."
            )

            self.logger.info(
                f"Train {train.train_id} waiting for "
                f"route {route.route_id}"
            )

            time.sleep(0.5)

        train.set_state(
            TrainState.ROUTE_GRANTED
        )

        print(
            f"{train.train_id}: Route "
            f"{route.route_id} granted."
        )

        self.logger.info(
            f"Train {train.train_id} granted route "
            f"{route.route_id}"
        )

        train.assign_route(
            route.track_ids
        )

        train.set_state(
            TrainState.MOVING
        )

        # Move through every track
        for track_id in route.track_ids:

            track = self.interlocking.network.get_track(
                track_id
            )

            if track is None:
                continue

            if track.occupy(train.train_id):

                train.current_track = track_id

                print(
                    f"{train.train_id} entered "
                    f"{track_id}"
                )

                self.logger.info(
                    f"Train {train.train_id} entered "
                    f"track {track_id}"
                )

                self.event_queue_publish(
                    EventType.TRAIN_MOVED,
                    train.train_id,
                    track_id,
                    f"{train.train_id} entered {track_id}"
                )

                # Defensive collision check
                collision_detected = (
                    self.check_for_collisions(train)
                )

                if collision_detected:

                    print(
                        f"!!! COLLISION WARNING: "
                        f"{train.train_id} !!!"
                    )

                    self.logger.warning(
                        f"Collision warning for train "
                        f"{train.train_id} on {track_id}"
                    )

                    self.collision_monitor.emergency_stop(
                        train
                    )

                    track.leave(
                        train.train_id
                    )

                    self.interlocking.release_route(
                        train.train_id,
                        route
                    )

                    train.current_track = None

                    print(
                        f"{train.train_id}: "
                        f"EMERGENCY STOP"
                    )

                    return

                # Simulate travel time
                travel_time = 1 / train.speed

                print(
                    f"{train.train_id} travelling on "
                    f"{track_id} "
                    f"(time={travel_time:.2f}s)"
                )

                time.sleep(travel_time)

                track.leave(
                    train.train_id
                )

                print(
                    f"{train.train_id} left "
                    f"{track_id}"
                )

                self.logger.info(
                    f"Train {train.train_id} left "
                    f"track {track_id}"
                )

                self.event_queue_publish(
                    EventType.TRACK_RELEASED,
                    train.train_id,
                    track_id,
                    f"{train.train_id} left {track_id}"
                )

        # Route completed
        self.interlocking.release_route(
            train.train_id,
            route
        )

        train.current_track = None

        train.set_state(
            TrainState.ARRIVED
        )

        print(
            f"{train.train_id} arrived at "
            f"{train.destination}."
        )

        self.logger.info(
            f"Train {train.train_id} arrived at "
            f"{train.destination}"
        )

        self.event_queue_publish(
            EventType.TRAIN_ARRIVED,
            train.train_id,
            message=(
                f"{train.train_id} arrived at "
                f"{train.destination}"
            )
        )

    def event_queue_publish(
        self,
        event_type,
        train_id=None,
        resource_id=None,
        message=""
    ):

        self.interlocking.event_queue.publish(
            Event(
                event_type=event_type,
                train_id=train_id,
                resource_id=resource_id,
                message=message
            )
        )

    def check_for_collisions(
        self,
        train: Train
    ) -> bool:

        for other_train in self.active_trains:

            if other_train is train:
                continue

            if self.collision_monitor.check_track_conflict(
                train,
                other_train
            ):
                return True

        return False

    def start_train(
        self,
        train: Train,
        route: Route
    ):

        train.thread = Thread(
            target=self.run_train,
            args=(train, route),
            name=f"TrainThread-{train.train_id}"
        )

        train.thread.start()

    def wait_for_train(
        self,
        train: Train
    ):

        if train.thread:
            train.thread.join()