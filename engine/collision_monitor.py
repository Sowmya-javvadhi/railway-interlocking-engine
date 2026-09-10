from models.train import Train, TrainState
from models.event import Event, EventType
from engine.event_queue import EventQueue


class CollisionMonitor:

    def __init__(self, event_queue: EventQueue):
        self.event_queue = event_queue

    def check_track_conflict(
        self,
        train: Train,
        other_train: Train
    ) -> bool:

        # No conflict if either train is not on a track
        if (
            train.current_track is None
            or other_train.current_track is None
        ):
            return False

        # Collision condition
        if train.current_track == other_train.current_track:

            train.set_state(
                TrainState.COLLISION_WARNING
            )

            other_train.set_state(
                TrainState.COLLISION_WARNING
            )

            self.event_queue.publish(
                Event(
                    event_type=EventType.COLLISION_WARNING,
                    train_id=train.train_id,
                    resource_id=train.current_track,
                    message=(
                        f"Possible collision detected "
                        f"between {train.train_id} "
                        f"and {other_train.train_id}"
                    )
                )
            )

            return True

        return False

    def emergency_stop(
        self,
        train: Train
    ):

        train.set_state(
            TrainState.EMERGENCY_STOP
        )

        self.event_queue.publish(
            Event(
                event_type=EventType.EMERGENCY_STOP,
                train_id=train.train_id,
                resource_id=train.current_track,
                message=(
                    f"Emergency stop activated for "
                    f"{train.train_id}"
                )
            )
        )