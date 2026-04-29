from typing import Dict, Any

class MigrationError(Exception):
    """Base exception for all migration-related errors."""
    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.context = context or {}

class MappingError(MigrationError):
    """Raised when there are issues with the YAML mapping configuration."""
    pass

class ConnectionError(MigrationError):
    """Raised when a database connection fails."""
    pass

class IntrospectionError(MigrationError):
    """Raised when schema introspection fails."""
    pass

class BatchFailedError(MigrationError):
    """Raised when a batch of data fails to commit."""
    pass

class ResumeError(MigrationError):
    """Raised when resuming a migration fails due to state issues."""
    pass
