import os
import time
import signal
import subprocess
import sys
from pathlib import Path

def run_crash_simulation():
    state_dir = Path("crash_test_state")
    state_dir.mkdir(exist_ok=True)
    state_file = state_dir / "crash_job.state.json"
    
    # Ensure a clean start with an initial valid state
    initial_content = '{"job_name": "crash_job", "last_pk": 0, "status": "running"}'
    state_file.write_text(initial_content)
    
    print(f"Initial state exists at {state_file}")
    
    # Script that will be killed
    script_content = f"""
import os
import time
import sys

# Monkeypatch os.replace BEFORE importing anything else
original_replace = os.replace
def slow_replace(src, dst):
    print("REPLACE_STARTING", flush=True)
    sys.stdout.flush()
    time.sleep(5)
    original_replace(src, dst)

os.replace = slow_replace

from sync_mail.state.checkpoint import Checkpoint

cp = Checkpoint("crash_job", state_dir="{state_dir}")
print("Saving new state...", flush=True)
cp.save(last_pk=100, batches_committed=1, rows_committed=100, source_table="s", target_table="t")
"""
    
    test_script = Path("crash_simulator.py")
    test_script.write_text(script_content)
    
    # Use -u for unbuffered output
    process = subprocess.Popen([sys.executable, "-u", str(test_script)], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True,
                              bufsize=1)
    
    # Wait for the script to reach the sleep part
    print("Waiting for script to reach the 'replace' phase...")
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(f"Script output: {line.strip()}")
        if "REPLACE_STARTING" in line:
            print("Detected replace phase. Killing process with SIGKILL (kill -9)...")
            process.kill() # SIGKILL
            break
            
    process.wait()
    
    # Check the state file
    print("Checking state file after crash...")
    content = state_file.read_text()
    
    if content == initial_content:
        print("SUCCESS: State file remained intact (atomic).")
    else:
        print(f"FAILURE: State file was modified. Content: {content}")
        
    # Cleanup
    test_script.unlink()
    for f in state_dir.glob("*"):
        f.unlink()
    state_dir.rmdir()

if __name__ == "__main__":
    run_crash_simulation()
