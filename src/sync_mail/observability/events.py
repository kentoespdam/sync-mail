import queue
from enum import Enum
from typing import Callable, Dict, Any, List

class EventType(Enum):
    JOB_STARTED = "JOB_STARTED"
    BATCH_COMMITTED = "BATCH_COMMITTED"
    BATCH_FAILED = "BATCH_FAILED"
    JOB_COMPLETED = "JOB_COMPLETED"
    JOB_ABORTED = "JOB_ABORTED"

class Event:
    """Represents an event published by the migration engine."""
    def __init__(self, event_type: EventType, payload: Dict[str, Any]):
        self.event_type = event_type
        self.payload = payload

class EventBus:
    """A minimal event bus for inter-module communication, especially between worker threads and the TUI."""
    def __init__(self):
        self._subscribers: List[Callable[[Event], None]] = []
        self._event_queue: queue.Queue[Event] = queue.Queue()

    def publish(self, event: Event):
        """
        Publishes an event to the bus.
        Events are added to an internal queue to be processed by subscribers.
        """
        if not isinstance(event, Event):
            raise TypeError("Can only publish Event objects.")
        self._event_queue.put(event)
        # In a real-time TUI scenario, a dedicated thread would pull from _event_queue
        # and dispatch to subscribers. For simplicity here, we might just call handlers directly
        # or rely on a background task to do so.
        # For this foundational step, we'll assume a mechanism exists to process the queue.
        # Let's simulate by directly calling subscribers for now, though a queue implies async processing.
        # A better approach for TUI would be a worker thread consuming the queue and updating the UI.
        # For now, let's just make it clear that events are queued.

    def subscribe(self, handler: Callable[[Event], None]):
        """
        Subscribes a handler function to receive events.
        The handler function must accept a single argument: an Event object.
        """
        if not callable(handler):
            raise TypeError("Handler must be a callable function.")
        self._subscribers.append(handler)

    def _process_queue(self):
        """Internal method to process events from the queue and dispatch to subscribers."""
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                for handler in self._subscribers:
                    try:
                        handler(event)
                    except Exception as e:
                        # Log or handle errors in handlers gracefully
                        print(f"Error in event handler {handler.__name__}: {e}", file=sys.stderr) # Basic error reporting
            except queue.Empty:
                break # Should not happen with get_nowait but good practice

# Global instance for simplicity, or could be managed by an application context
event_bus = EventBus()

# Example usage:
# def my_handler(event: Event):
#     print(f"Received event: {event.event_type.name} with payload {event.payload}")
#
# event_bus.subscribe(my_handler)
#
# event_bus.publish(Event(EventType.JOB_STARTED, {"job_name": "migration_1", "total_rows": 1000000}))
# event_bus.publish(Event(EventType.BATCH_COMMITTED, {"job_name": "migration_1", "batch_id": 1, "rows": 1000, "last_pk": 1000}))
#
# event_bus._process_queue() # Manually call to simulate processing for testing
