import pytest
import os
import json
from pathlib import Path
from sync_mail.state.checkpoint import Checkpoint
from sync_mail.errors import ResumeError

def test_checkpoint_save_load(tmp_path):
    state_dir = tmp_path / "state"
    cp = Checkpoint("test-job", state_dir=str(state_dir))
    
    cp.save(
        last_pk=100,
        batches_committed=5,
        rows_committed=500,
        source_table="src",
        target_table="tgt",
        status="running"
    )
    
    state = cp.load()
    assert state["job_name"] == "test-job"
    assert state["last_pk"] == 100
    assert state["status"] == "running"
    assert state["rows_committed"] == 500

def test_checkpoint_atomic_write(tmp_path, mocker):
    state_dir = tmp_path / "state"
    cp = Checkpoint("test-job", state_dir=str(state_dir))
    
    # Mock os.replace to fail
    mocker.patch("os.replace", side_effect=OSError("Disk Full"))
    
    with pytest.raises(ResumeError):
        cp.save(100, 5, 500, "s", "t")
        
    # Ensure original file (if it existed) is not corrupted and temp is cleaned
    state_file = state_dir / "test-job.state.json"
    temp_file = state_dir / "test-job.state.json.tmp"
    assert not state_file.exists()
    assert not temp_file.exists()

def test_checkpoint_corrupt_json(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state_file = state_dir / "test-job.state.json"
    with open(state_file, "w") as f:
        f.write("{invalid json")
        
    cp = Checkpoint("test-job", state_dir=str(state_dir))
    with pytest.raises(ResumeError) as exc:
        cp.load()
    assert "corrupt" in str(exc.value)

def test_checkpoint_lock(tmp_path):
    state_dir = tmp_path / "state"
    cp1 = Checkpoint("test-job", state_dir=str(state_dir))
    cp2 = Checkpoint("test-job", state_dir=str(state_dir))
    
    cp1.acquire_lock()
    
    with pytest.raises(ResumeError) as exc:
        cp2.acquire_lock()
    assert "already being processed" in str(exc.value)
    
    cp1.release_lock()
    cp2.acquire_lock() # Should work now
    cp2.release_lock()
