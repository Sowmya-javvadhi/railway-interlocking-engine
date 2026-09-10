from queue import Queue
from threading import Lock

from models.event import Event


class EventQueue:

    def __init__(self):

        self._queue = Queue()

        self.history = []

        self.history_lock = Lock()


    def publish(self, event: Event):

        self._queue.put(event)

        with self.history_lock:

            self.history.append(event)


    def get(self) -> Event:

        return self._queue.get()


    def task_done(self):

        self._queue.task_done()


    def empty(self) -> bool:

        return self._queue.empty()


    def size(self) -> int:

        return self._queue.qsize()


    def join(self):

        self._queue.join()


    def get_history(self, limit: int = 20):

        with self.history_lock:

            return list(self.history[-limit:])