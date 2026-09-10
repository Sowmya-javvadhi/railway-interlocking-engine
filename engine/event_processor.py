import threading

from engine.event_queue import EventQueue


class EventProcessor:

    def __init__(self, event_queue: EventQueue):

        self.event_queue = event_queue

        self.running = False

        self.thread = None

    def process_events(self):

        while self.running:

            try:
                event = self.event_queue.get()

                print(
                    f"[EVENT] {event}"
                )

                self.event_queue.task_done()

            except Exception as e:

                print(
                    f"Event processing error: {e}"
                )

    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self.process_events,
            name="EventProcessorThread",
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False