import signal
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from sync_mail.config.loader import load_mapping
from sync_mail.state.checkpoint import Checkpoint
from sync_mail.pipeline import extract, transform, load
from sync_mail.observability import event_bus, Event, EventType, logger
from sync_mail.db.connection import connect, transaction
from sync_mail.observability.metrics import ThroughputCalculator, compute_eta
from sync_mail.errors import ResumeError, MappingError, ConnectionError, BatchFailedError

class MigrationJob:
    """
    Orchestrates the end-to-end migration process.
    Handles loading mapping, checkpointing, ETL loop, and graceful shutdown.
    """
    def __init__(
        self, 
        job_name: str, 
        mapping_path: str, 
        source_dsn: Dict[str, Any], 
        target_dsn: Dict[str, Any]
    ):
        self.job_name = job_name
        self.mapping_path = mapping_path
        self.source_dsn = source_dsn
        self.target_dsn = target_dsn
        self.checkpoint = Checkpoint(job_name)
        self.metrics = ThroughputCalculator()
        self._should_abort = False
        self._start_time = None

    def _setup_signals(self):
        """Registers signal handlers for graceful shutdown."""
        def handle_signal(signum, frame):
            logger.warning(f"Received signal {signum}. Requesting graceful shutdown...")
            self._should_abort = True

        self._old_sigint = signal.signal(signal.SIGINT, handle_signal)
        self._old_sigterm = signal.signal(signal.SIGTERM, handle_signal)

    def _restore_signals(self):
        """Restores original signal handlers."""
        signal.signal(signal.SIGINT, self._old_sigint)
        signal.signal(signal.SIGTERM, self._old_sigterm)

    def run(self):
        """
        Executes the migration job.
        """
        self._setup_signals()
        conn_source = None
        conn_target = None
        state = {}
        
        try:
            # 1. Load Mapping
            mapping = load_mapping(self.mapping_path)
            
            # 2. Check Resume Condition
            state = self.checkpoint.load()
            if state.get("status") == "completed":
                event_bus.publish(Event(EventType.JOB_COMPLETED, {
                    "job_name": self.job_name,
                    "message": "Job already completed previously."
                }))
                return

            if state:
                # Verify consistency
                if (state.get("source_table") != mapping.source_table or 
                    state.get("target_table") != mapping.target_table):
                    raise ResumeError(
                        "State mismatch: source/target tables in state.json do not match mapping.",
                        context={
                            "state_source": state.get("source_table"),
                            "mapping_source": mapping.source_table,
                            "state_target": state.get("target_table"),
                            "mapping_target": mapping.target_table
                        }
                    )
                logger.info(f"Resuming job '{self.job_name}' from PK {state['last_pk']}")
            else:
                logger.info(f"Starting new job '{self.job_name}'")
                state = {
                    "job_name": self.job_name,
                    "last_pk": 0,
                    "batches_committed": 0,
                    "rows_committed": 0,
                    "source_table": mapping.source_table,
                    "target_table": mapping.target_table,
                    "started_at": datetime.now(timezone.utc).isoformat()
                }

            # 3. Open Connections
            conn_source = connect("source", self.source_dsn)
            conn_target = connect("target", self.target_dsn)
            
            self.checkpoint.acquire_lock()
            
            # 4. Estimate total rows
            total_rows_est = 0
            with conn_source.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) as cnt FROM `{mapping.source_table}` WHERE `{mapping.pk_column}` > %s", (state["last_pk"],))
                total_rows_est = cursor.fetchone()["cnt"]

            event_bus.publish(Event(EventType.JOB_STARTED, {
                "job_name": self.job_name,
                "source_table": mapping.source_table,
                "target_table": mapping.target_table,
                "total_rows_est": total_rows_est,
                "last_pk": state["last_pk"]
            }))

            self._start_time = time.monotonic()
            
            # 5. Batch Loop
            for batch_idx, batch_rows in enumerate(extract(conn_source, mapping, state["last_pk"])):
                if self._should_abort:
                    self.checkpoint.mark_aborted(state, "User interrupt")
                    event_bus.publish(Event(EventType.JOB_ABORTED, {
                        "job_name": self.job_name,
                        "reason": "User interrupt",
                        "last_pk": state["last_pk"]
                    }))
                    return

                # Transform
                transformed = transform(batch_rows, mapping)
                
                # Load (Atomic)
                with transaction(conn_target):
                    rows_loaded = load(conn_target, mapping, transformed)
                
                # Update State
                rows_in_batch = len(batch_rows)
                state["last_pk"] = batch_rows[-1][mapping.pk_column]
                state["batches_committed"] += 1
                state["rows_committed"] += rows_loaded
                
                self.metrics.record(rows_in_batch)
                throughput = self.metrics.current_rate()
                remaining = max(0, total_rows_est - (state["rows_committed"])) 
                
                eta = compute_eta(remaining, throughput)
                
                self.checkpoint.save(
                    last_pk=state["last_pk"],
                    batches_committed=state["batches_committed"],
                    rows_committed=state["rows_committed"],
                    source_table=mapping.source_table,
                    target_table=mapping.target_table,
                    status="running",
                    started_at=state.get("started_at")
                )
                
                event_bus.publish(Event(EventType.BATCH_COMMITTED, {
                    "job_name": self.job_name,
                    "batch_id": state["batches_committed"],
                    "rows": rows_loaded,
                    "last_pk": state["last_pk"],
                    "throughput": throughput,
                    "eta": str(eta) if eta else "Unknown"
                }))

            # 6. Success
            self.checkpoint.mark_completed(state)
            duration = time.monotonic() - self._start_time
            event_bus.publish(Event(EventType.JOB_COMPLETED, {
                "job_name": self.job_name,
                "total_rows": state["rows_committed"],
                "duration_sec": duration
            }))

        except Exception as e:
            logger.exception(f"Job '{self.job_name}' failed: {e}")
            reason = str(e)
            if state:
                self.checkpoint.mark_aborted(state, reason)
            event_bus.publish(Event(EventType.JOB_ABORTED, {
                "job_name": self.job_name,
                "reason": reason,
                "error_type": type(e).__name__
            }))
            # Re-raise for outer handlers if any
            raise

        finally:
            self.checkpoint.release_lock()
            if conn_source:
                conn_source.close()
            if conn_target:
                conn_target.close()
            self._restore_signals()

class JobBatch:
    """
    Executes multiple MigrationJobs sequentially.
    """
    def __init__(self, jobs: List[MigrationJob], stop_on_failure: bool = False):
        self.jobs = jobs
        self.stop_on_failure = stop_on_failure

    def run(self):
        total_jobs = len(self.jobs)
        success_count = 0
        failure_count = 0
        
        for idx, job in enumerate(self.jobs):
            event_bus.publish(Event(EventType.MULTI_JOB_PROGRESS, {
                "current_job_index": idx + 1,
                "total_jobs": total_jobs,
                "current_job_name": job.job_name,
                "success_count": success_count,
                "failure_count": failure_count
            }))
            
            try:
                job.run()
                success_count += 1
            except Exception as e:
                failure_count += 1
                if self.stop_on_failure:
                    logger.error(f"Batch aborted due to failure in job '{job.job_name}': {e}")
                    raise
                else:
                    logger.warning(f"Job '{job.job_name}' failed, continuing batch: {e}")
                    
        event_bus.publish(Event(EventType.MULTI_JOB_PROGRESS, {
            "current_job_index": total_jobs,
            "total_jobs": total_jobs,
            "current_job_name": "Completed",
            "success_count": success_count,
            "failure_count": failure_count,
            "is_done": True
        }))
