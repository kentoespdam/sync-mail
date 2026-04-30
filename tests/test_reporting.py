# tests/test_reporting.py

import os
import pytest
from datetime import datetime
from sync_mail.pipeline.reporter import HTMLReportGenerator, JobReportData
from sync_mail.observability import event_bus, Event, EventType

@pytest.fixture
def reporter(tmp_path):
    output_dir = tmp_path / "reports"
    return HTMLReportGenerator(output_dir=str(output_dir))

def test_single_job_report_generation(reporter, tmp_path):
    # Simulate events for a single job
    job_name = "test_job"
    
    event_bus.publish(Event(EventType.JOB_STARTED, {
        "job_name": job_name,
        "source_table": "src_table",
        "target_table": "tgt_table",
        "source_host": "localhost",
        "source_db": "src_db",
        "target_host": "remote_host",
        "target_db": "tgt_db"
    }))
    
    event_bus.publish(Event(EventType.BATCH_COMMITTED, {
        "job_name": job_name,
        "rows": 100,
        "throughput": 10.0,
        "eta": "0:01"
    }))
    
    # We need to wait a bit because EventBus is async
    import time
    time.sleep(0.5)
    
    event_bus.publish(Event(EventType.JOB_COMPLETED, {
        "job_name": job_name,
        "total_rows": 100,
        "duration_sec": 1.0
    }))
    
    time.sleep(0.5)
    
    # Check if report was generated
    files = os.listdir(reporter.output_dir)
    assert len(files) == 1
    assert files[0].startswith("real-sync_src_table_")
    assert files[0].endswith(".html")
    
    # Read and check content
    with open(os.path.join(reporter.output_dir, files[0]), "r") as f:
        content = f.read()
        assert "test_job" in content
        assert "src_table" in content
        assert "tgt_table" in content
        assert "100" in content
        assert "SUCCESS" in content

def test_dry_run_report_generation(reporter, tmp_path):
    # Simulate dry run completion
    report_dict = {
        "job_name": "dry_run_job",
        "source": "src_t",
        "target": "tgt_t",
        "sample_limit": 10,
        "rows_extracted": 10,
        "status": "PASS",
        "source_host": "src_host",
        "source_db": "src_db",
        "target_host": "tgt_host",
        "target_db": "tgt_db",
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "anomalies": [
            {
                "category": "Data Type Mismatch",
                "severity": "BLOCKER",
                "column": "age",
                "row_pk": 1,
                "raw_value": "NULL",
                "message": "Column cannot be NULL",
                "recommendation": "Set default value"
            }
        ],
        "recommendations": ["Set default value"]
    }
    
    event_bus.publish(Event(EventType.DRY_RUN_COMPLETED, {
        "job_name": "dry_run_job",
        "report": report_dict
    }))
    
    import time
    time.sleep(0.5)
    
    files = os.listdir(reporter.output_dir)
    assert len(files) == 1
    assert files[0].startswith("dry-run_src_t_")

    with open(os.path.join(reporter.output_dir, files[0]), "r") as f:
        content = f.read()
        assert "MODE SIMULASI" in content
        assert "DRY RUN" in content
        assert "Set default value" in content
        assert "BLOCKER" in content
    
def test_batch_report_generation(reporter, tmp_path):
    # Simulate batch events
    event_bus.publish(Event(EventType.MULTI_JOB_PROGRESS, {
        "current_job_index": 1,
        "total_jobs": 2,
        "current_job_name": "job1",
        "success_count": 0,
        "failure_count": 0
    }))
    
    event_bus.publish(Event(EventType.JOB_STARTED, {
        "job_name": "job1",
        "source_table": "table1",
        "target_table": "target1",
        "source_host": "h1",
        "source_db": "d1",
        "target_host": "h2",
        "target_db": "d2"
    }))
    
    import time
    time.sleep(0.1)
    
    event_bus.publish(Event(EventType.JOB_COMPLETED, {
        "job_name": "job1",
        "total_rows": 50,
        "duration_sec": 0.5
    }))
    
    time.sleep(0.1)
    
    event_bus.publish(Event(EventType.MULTI_JOB_PROGRESS, {
        "current_job_index": 2,
        "total_jobs": 2,
        "current_job_name": "job2",
        "success_count": 1,
        "failure_count": 0
    }))
    
    event_bus.publish(Event(EventType.JOB_STARTED, {
        "job_name": "job2",
        "source_table": "table2",
        "target_table": "target2",
        "source_host": "h1",
        "source_db": "d1",
        "target_host": "h2",
        "target_db": "d2"
    }))
    
    time.sleep(0.1)
    
    event_bus.publish(Event(EventType.JOB_COMPLETED, {
        "job_name": "job2",
        "total_rows": 50,
        "duration_sec": 0.5
    }))
    
    time.sleep(0.1)
    
    event_bus.publish(Event(EventType.MULTI_JOB_PROGRESS, {
        "current_job_index": 2,
        "total_jobs": 2,
        "current_job_name": "Completed",
        "success_count": 2,
        "failure_count": 0,
        "is_done": True
    }))
    
    time.sleep(0.5)
    
    files = os.listdir(reporter.output_dir)
    assert len(files) == 1
    assert files[0].startswith("batch_multi_")
    
    with open(os.path.join(reporter.output_dir, files[0]), "r") as f:
        content = f.read()
        assert "Sync-Mail Batch Migration Summary" in content
        assert "job1" in content
        assert "job2" in content
        assert "table1" in content
        assert "table2" in content
