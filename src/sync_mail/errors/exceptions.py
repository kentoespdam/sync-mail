from typing import Dict, Any, Optional

class MigrationError(Exception):
    """
    Base exception for all domain-specific errors in sync-mail.
    Carries an optional context dictionary for structured logging/debugging.
    """
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}

class MappingError(MigrationError):
    """Raised when there are issues with YAML mapping configuration or validation."""
    pass

class ConnectionError(MigrationError):
    """Raised when database connection fails (source or target)."""
    pass

class IntrospectionError(MigrationError):
    """Raised when reading database schema from information_schema fails."""
    pass

class BatchFailedError(MigrationError):
    """Raised when a data batch transaction fails to commit."""
    pass

class ResumeError(MigrationError):
    """Raised when resuming from a checkpoint fails (e.g., corrupt state.json)."""
    pass

class ConfigError(MigrationError):
    """Raised when there are issues with general configuration files (e.g., connection.yaml)."""
    pass
