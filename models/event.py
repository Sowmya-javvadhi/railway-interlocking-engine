from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventType(Enum):
    TRAIN_CREATED = "TRAIN_CREATED"
    TRAIN_STARTED = "TRAIN_STARTED"
    ROUTE_REQUESTED = "ROUTE_REQUESTED"
    ROUTE_GRANTED = "ROUTE_GRANTED"
    ROUTE_REJECTED = "ROUTE_REJECTED"
    TRACK_RESERVED = "TRACK_RESERVED"
    TRAIN_MOVED = "TRAIN_MOVED"
    TRACK_RELEASED = "TRACK_RELEASED"
    SIGNAL_CHANGED = "SIGNAL_CHANGED"
    COLLISION_WARNING = "COLLISION_WARNING"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    TRAIN_ARRIVED = "TRAIN_ARRIVED"


@dataclass
class Event:
    event_type: EventType
    train_id: str | None = None
    resource_id: str | None = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return (
            f"[{self.timestamp.strftime('%H:%M:%S')}] "
            f"{self.event_type.value} | "
            f"Train={self.train_id} | "
            f"Resource={self.resource_id} | "
            f"{self.message}"
        )