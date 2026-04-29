import queue
import threading
from enum import Enum
from typing import Dict, Any, Callable, List, Optional

class EventType(Enum):
    """Types of events that can be published to the EventBus."""
    JOB_STARTED = "JobStarted"
    BATCH_COMMITTED = "BatchCommitted"
    BATCH_FAILED = "BatchFailed"
    JOB_COMPLETED = "JobCompleted"
    JOB_ABORTED = "JobAborted"
    MULTI_JOB_PROGRESS = "MultiJobProgress"

class Event:
    """A migration event with a type and a structured payload."""
    def __init__(self, event_type: EventType, payload: Dict[str, Any]):
        self.type = event_type
        self.payload = payload

class EventBus:
    """
    A thread-safe event bus for communication between worker threads and the UI.
    Uses an internal queue to decouple publishers from subscribers.
    """
    def __init__(self):
        self._queue: queue.Queue[Event] = queue.Queue()
        self._subscribers: List[Callable[[Event], None]] = []
        self._lock = threading.Lock()
        self._dispatch_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _dispatch_loop(self):
        """Internal loop to process and dispatch events from the queue."""
        while not self._stop_event.is_set():
            try:
                # Use a small timeout to allow checking stop_event
                event = self._queue.get(timeout=0.1)
                
                with self._lock:
                    handlers = list(self._subscribers)
                
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception:
                        # Silently ignore handler errors to prevent bus crash
                        # In production, we might log this to a separate internal logger
                        pass
                
                self._queue.task_done()
            except queue.Empty:
                continue

    def start(self):
        """Starts the background dispatch thread."""
        with self._lock:
            if self._dispatch_thread is None or not self._dispatch_thread.is_alive():
                self._stop_event.clear()
                self._dispatch_thread = threading.Thread(
                    target=self._dispatch_loop, 
                    name="EventBusDispatcher",
                    daemon=True
                )
                self._dispatch_thread.start()

    def stop(self):
        """Stops the background dispatch thread."""
        self._stop_event.set()
        if self._dispatch_thread:
            self._dispatch_thread.join(timeout=1.0)

    def publish(self, event: Event):
        """Publishes an event to the bus."""
        if not isinstance(event, Event):
            raise TypeError("Only Event objects can be published.")
        self._queue.put(event)

    def subscribe(self, handler: Callable[[Event], None]):
        """Subscribes a callback handler to receive events."""
        if not callable(handler):
            raise TypeError("Handler must be a callable.")
        with self._lock:
            self._subscribers.append(handler)
        
        # Ensure dispatcher is running when someone subscribes
        self.start()

# Singleton instance for application-wide use
event_bus = EventBus()
