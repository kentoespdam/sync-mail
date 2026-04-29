import unittest
from unittest.mock import patch, MagicMock, call
import json
import os
from pathlib import Path
from sync_mail.pipeline.orchestrator import MigrationJob
from sync_mail.errors import ResumeError
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.observability import event_bus, EventType

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.job_name = "test_job"
        self.mapping_path = "tests/test_mapping.yaml"
        self.source_dsn = {"host": "src_host"}
        self.target_dsn = {"host": "dst_host"}
        
        # Create a dummy mapping file
        self.mapping_data = {
            "migration_job": {
                "source_table": "src_table",
                "target_table": "dst_table",
                "pk_column": "id",
                "batch_size": 10000,
                "mappings": [
                    {"target_column": "id", "source_column": "id", "transformation_type": "NONE"},
                    {"target_column": "name", "source_column": "name", "transformation_type": "NONE"}
                ]
            }
        }
        with open(self.mapping_path, "w") as f:
            json.dump(self.mapping_data, f)

        # Ensure state dir exists and is empty
        self.state_dir = Path("state")
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / f"{self.job_name}.state.json"
        if self.state_file.exists():
            self.state_file.unlink()

    def tearDown(self):
        if os.path.exists(self.mapping_path):
            os.remove(self.mapping_path)
        if self.state_file.exists():
            self.state_file.unlink()

    @patch("sync_mail.pipeline.orchestrator.connect")
    @patch("sync_mail.pipeline.orchestrator.extract")
    @patch("sync_mail.pipeline.orchestrator.transform")
    @patch("sync_mail.pipeline.orchestrator.load")
    @patch("sync_mail.pipeline.orchestrator.event_bus")
    def test_run_success(self, mock_event_bus, mock_load, mock_transform, mock_extract, mock_connect):
        # Setup mocks
        mock_conn_src = MagicMock()
        mock_conn_dst = MagicMock()
        mock_connect.side_effect = [mock_conn_src, mock_conn_dst]
        
        mock_cursor = mock_conn_src.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = {"cnt": 25}
        
        # Mock extract yielding 3 batches
        batch1 = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
        batch2 = [{"id": 3, "name": "c"}, {"id": 4, "name": "d"}]
        batch3 = [{"id": 5, "name": "e"}]
        mock_extract.return_value = iter([batch1, batch2, batch3])
        
        mock_transform.side_effect = lambda rows, mapping: [tuple(r.values()) for r in rows]
        mock_load.side_effect = [2, 2, 1]
        
        # Run job
        job = MigrationJob(self.job_name, self.mapping_path, self.source_dsn, self.target_dsn)
        job.run()
        
        # Verify calls
        self.assertEqual(mock_connect.call_count, 2)
        self.assertEqual(mock_extract.call_count, 1)
        self.assertEqual(mock_transform.call_count, 3)
        self.assertEqual(mock_load.call_count, 3)
        
        # Verify checkpoint state
        with open(self.state_file, "r") as f:
            state = json.load(f)
            self.assertEqual(state["status"], "completed")
            self.assertEqual(state["last_pk"], 5)
            self.assertEqual(state["rows_committed"], 5)
            self.assertEqual(state["batches_committed"], 3)

        # Verify event bus calls
        mock_event_bus.publish.assert_any_call(unittest.mock.ANY) # Check for JOB_STARTED, BATCH_COMMITTED, etc.
        
    @patch("sync_mail.pipeline.orchestrator.connect")
    @patch("sync_mail.pipeline.orchestrator.extract")
    def test_run_resume_mismatch(self, mock_extract, mock_connect):
        # Create a state file with different tables
        with open(self.state_file, "w") as f:
            json.dump({
                "job_name": self.job_name,
                "source_table": "wrong_src",
                "target_table": "dst_table",
                "last_pk": 100,
                "status": "aborted",
                "batches_committed": 10,
                "rows_committed": 100
            }, f)
            
        job = MigrationJob(self.job_name, self.mapping_path, self.source_dsn, self.target_dsn)
        with self.assertRaises(ResumeError):
            job.run()

if __name__ == "__main__":
    unittest.main()
