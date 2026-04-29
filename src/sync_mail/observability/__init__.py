# src/sync_mail/observability/__init__.py

from .events import event_bus, Event, EventType
from .logger import configure_logging
import logging

# Standard logger for the package
logger = logging.getLogger("sync_mail")
