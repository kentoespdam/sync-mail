import os
import json
import fcntl
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

from sync_mail.errors import ResumeError

logger = logging.getLogger(__name__)

class Checkpoint:
    """
    Manages migration state persistence and process locking.
    Uses an atomic write pattern (write-temp + replace) to ensure state integrity.
    """

    def __init__(self, job_name: str, state_dir: str = "state"):
        self.job_name = job_name
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / f"{job_name}.state.json"
        self.lock_file = self.state_dir / f"{job_name}.lock"
        self._lock_fd: Optional[int] = None

        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def acquire_lock(self):
        """
        Acquires an exclusive lock on the lock file to prevent multiple processes
        from running the same job.
        """
        if self._lock_fd is not None:
            return

        try:
            # Open or create the lock file
            self._lock_fd = os.open(self.lock_file, os.O_RDWR | os.O_CREAT)
            # Try to acquire exclusive lock without blocking
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write PID to lock file for debugging
            os.ftruncate(self._lock_fd, 0)
            os.lseek(self._lock_fd, 0, os.SEEK_SET)
            os.write(self._lock_fd, str(os.getpid()).encode())
            
        except (IOError, OSError) as e:
            if self._lock_fd is not None:
                os.close(self._lock_fd)
                self._lock_fd = None
            raise ResumeError(
                f"Job '{self.job_name}' is already being processed by another process.",
                context={"job_name": self.job_name, "error": str(e)}
            ) from e

    def release_lock(self):
        """Releases the process lock."""
        if self._lock_fd is not None:
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
            except OSError:
                pass
            finally:
                self._lock_fd = None

    def load(self) -> Dict[str, Any]:
        """
        Loads the state from the JSON file.
        Returns an empty dict if the file doesn't exist.
        Raises ResumeError if the file is corrupt or missing required fields.
        """
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
        except json.JSONDecodeError as e:
            raise ResumeError(
                f"State file for job '{self.job_name}' is corrupt and cannot be parsed.",
                context={"job_name": self.job_name, "path": str(self.state_file), "error": str(e)}
            ) from e
        except Exception as e:
            raise ResumeError(
                f"Failed to read state file for job '{self.job_name}'.",
                context={"job_name": self.job_name, "path": str(self.state_file), "error": str(e)}
            ) from e

        # Validate minimum required fields if state is not empty
        required_fields = ["job_name", "last_pk", "status"]
        missing = [f for f in required_fields if f not in state]
        if missing:
            raise ResumeError(
                f"State file for job '{self.job_name}' is missing required fields: {', '.join(missing)}.",
                context={"job_name": self.job_name, "missing_fields": missing}
            )

        return state

    def save(
        self,
        last_pk: Any,
        batches_committed: int,
        rows_committed: int,
        source_table: str,
        target_table: str,
        status: str = "running",
        error: Optional[str] = None,
        started_at: Optional[str] = None
    ):
        """
        Saves the state atomically using a temporary file and os.replace().
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Prepare state data
        data = {
            "job_name": self.job_name,
            "source_table": source_table,
            "target_table": target_table,
            "last_pk": last_pk,
            "batches_committed": batches_committed,
            "rows_committed": rows_committed,
            "status": status,
            "started_at": started_at or now,
            "updated_at": now,
            "error": error
        }

        temp_file = self.state_file.with_suffix(".json.tmp")
        
        try:
            with open(temp_file, "w") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic rename
            os.replace(temp_file, self.state_file)
            logger.debug(f"State saved for job '{self.job_name}' at PK {last_pk}")
            
        except Exception as e:
            if temp_file.exists():
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise ResumeError(
                f"Failed to save state for job '{self.job_name}' atomically.",
                context={"job_name": self.job_name, "error": str(e)}
            ) from e

    def mark_completed(self, state: Dict[str, Any]):
        """Marks the job as completed."""
        self.save(
            last_pk=state["last_pk"],
            batches_committed=state["batches_committed"],
            rows_committed=state["rows_committed"],
            source_table=state["source_table"],
            target_table=state["target_table"],
            status="completed",
            started_at=state.get("started_at")
        )

    def mark_aborted(self, state: Dict[str, Any], reason: str):
        """Marks the job as aborted with a reason."""
        self.save(
            last_pk=state["last_pk"],
            batches_committed=state["batches_committed"],
            rows_committed=state["rows_committed"],
            source_table=state["source_table"],
            target_table=state["target_table"],
            status="aborted",
            error=reason,
            started_at=state.get("started_at")
        )

    def __del__(self):
        self.release_lock()
