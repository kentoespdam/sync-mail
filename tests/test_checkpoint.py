import os
import json
import pytest
import shutil
from pathlib import Path
from sync_mail.state.checkpoint import Checkpoint
from sync_mail.errors import ResumeError

@pytest.fixture
def temp_state_dir(tmp_path):
    """Fixture to provide a clean temporary state directory."""
    return tmp_path / "state"

def test_load_non_existent(temp_state_dir):
    cp = Checkpoint("job1", state_dir=str(temp_state_dir))
    state = cp.load()
    assert state == {}

def test_save_load_roundtrip(temp_state_dir):
    cp = Checkpoint("job2", state_dir=str(temp_state_dir))
    cp.save(
        last_pk=12345,
        batches_committed=10,
        rows_committed=1000,
        source_table="users_legacy",
        target_table="users_new",
        status="running"
    )
    
    state = cp.load()
    assert state["job_name"] == "job2"
    assert state["last_pk"] == 12345
    assert state["batches_committed"] == 10
    assert state["rows_committed"] == 1000
    assert state["status"] == "running"
    assert "updated_at" in state
    assert "started_at" in state

def test_mark_completed(temp_state_dir):
    cp = Checkpoint("job3", state_dir=str(temp_state_dir))
    initial_state = {
        "last_pk": 500,
        "batches_committed": 5,
        "rows_committed": 500,
        "source_table": "src",
        "target_table": "dst",
        "started_at": "2026-01-01T00:00:00Z"
    }
    cp.mark_completed(initial_state)
    
    state = cp.load()
    assert state["status"] == "completed"
    assert state["last_pk"] == 500
    assert state["started_at"] == "2026-01-01T00:00:00Z"

def test_mark_aborted(temp_state_dir):
    cp = Checkpoint("job4", state_dir=str(temp_state_dir))
    initial_state = {
        "last_pk": 999,
        "batches_committed": 9,
        "rows_committed": 900,
        "source_table": "src",
        "target_table": "dst"
    }
    cp.mark_aborted(initial_state, "connection timeout")
    
    state = cp.load()
    assert state["status"] == "aborted"
    assert state["error"] == "connection timeout"

def test_corrupt_state_raises_resume_error(temp_state_dir):
    cp = Checkpoint("job5", state_dir=str(temp_state_dir))
    temp_state_dir.mkdir(parents=True, exist_ok=True)
    state_file = temp_state_dir / "job5.state.json"
    state_file.write_text("{ invalid json }")
    
    with pytest.raises(ResumeError) as excinfo:
        cp.load()
    assert "corrupt" in str(excinfo.value)

def test_missing_fields_raises_resume_error(temp_state_dir):
    cp = Checkpoint("job6", state_dir=str(temp_state_dir))
    temp_state_dir.mkdir(parents=True, exist_ok=True)
    state_file = temp_state_dir / "job6.state.json"
    state_file.write_text(json.dumps({"job_name": "job6"})) # last_pk and status missing
    
    with pytest.raises(ResumeError) as excinfo:
        cp.load()
    assert "missing required fields" in str(excinfo.value)

def test_lock_acquisition(temp_state_dir):
    cp1 = Checkpoint("locked_job", state_dir=str(temp_state_dir))
    cp1.acquire_lock()
    
    cp2 = Checkpoint("locked_job", state_dir=str(temp_state_dir))
    with pytest.raises(ResumeError) as excinfo:
        cp2.acquire_lock()
    assert "already being processed" in str(excinfo.value)
    
    cp1.release_lock()
    # Now cp2 should be able to acquire it
    cp2.acquire_lock()
    cp2.release_lock()

def test_atomic_write_preserves_old_on_failure(temp_state_dir, monkeypatch):
    cp = Checkpoint("job_atomic", state_dir=str(temp_state_dir))
    cp.save(1, 1, 1, "s", "t", "running")
    
    # Mock json.dump to raise an error
    import json
    def mock_dump(*args, **kwargs):
        raise RuntimeError("Disk full simulation")
    
    monkeypatch.setattr(json, "dump", mock_dump)
    
    with pytest.raises(ResumeError):
        cp.save(2, 2, 2, "s", "t", "running")
    
    # Verify old state is still there
    state = cp.load()
    assert state["last_pk"] == 1
    
    # Ensure tmp file is cleaned up
    tmp_file = temp_state_dir / "job_atomic.state.json.tmp"
    assert not tmp_file.exists()
