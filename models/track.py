from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Track:
    track_id: str
    source: str
    destination: str

    occupied_by: str | None = None
    reserved_by: str | None = None

    lock: Lock = field(default_factory=Lock, repr=False)

    def is_available(self) -> bool:
        return (
            self.occupied_by is None
            and self.reserved_by is None
        )

    def reserve(self, train_id: str) -> bool:
        with self.lock:
            if not self.is_available():
                return False

            self.reserved_by = train_id
            return True

    def release(self, train_id: str) -> bool:
        with self.lock:
            if self.reserved_by != train_id:
                return False

            self.reserved_by = None
            return True

    def occupy(self, train_id: str) -> bool:
        with self.lock:
            if self.reserved_by != train_id:
                return False

            self.reserved_by = None
            self.occupied_by = train_id
            return True

    def leave(self, train_id: str) -> bool:
        with self.lock:
            if self.occupied_by != train_id:
                return False

            self.occupied_by = None
            return True