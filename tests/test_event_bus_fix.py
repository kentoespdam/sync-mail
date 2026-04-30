
import pytest
from unittest.mock import MagicMock, patch
from sync_mail.observability import event_bus, Event, EventType
from sync_mail.pipeline.dry_run import DryRunEngine
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.db.target_probe import ColumnMetadata

def test_event_bus_integration_smoke():
    """
    Smoke test to ensure that calling event_bus.publish(Event(...)) 
    doesn't raise AttributeError in DryRunEngine.
    """
    mapping = MappingDocument(
        source_table="test",
        target_table="test",
        pk_column="id",
        mappings=[ColumnMapping(source_column="id", target_column="id")]
    )
    
    metadata = {
        "id": ColumnMetadata(
            name="id", 
            data_type="INT", 
            is_nullable=False,
            default=None,
            max_length=None,
            enum_values=None,
            column_type="int(11)"
        )
    }
    
    conn_source = MagicMock()
    conn_target = MagicMock()
    
    # Mock source data
    mock_cursor = conn_source.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.side_effect = [[{"id": 1}], []]
    
    # We want to use the real event_bus but maybe capture what it publishes if needed.
    # But the main goal is just to see if it blows up.
    
    with patch("sync_mail.pipeline.dry_run.describe_target_columns", return_value=metadata):
        engine = DryRunEngine(conn_source, conn_target, "test_schema", mapping, sample_limit=1)
        # This call used to trigger AttributeError at the very beginning (DRY_RUN_STARTED)
        report = engine.execute()
        
        assert report.rows_extracted == 1
        assert report.status == "PASS"

def test_manual_event_publish():
    """Manual check that the fixed pattern works."""
    event = Event(EventType.JOB_STARTED, {"test": "data"})
    event_bus.publish(event)
    # If we reach here, no AttributeError was raised.

def test_event_bus_attribute_error_repro():
    """
    Confirms that accessing Event as an attribute of event_bus raises AttributeError.
    This was the root cause of the reported blocker.
    """
    with pytest.raises(AttributeError) as excinfo:
        # This is the incorrect pattern reported in plan/bug/
        getattr(event_bus, "Event")
    
    assert "'EventBus' object has no attribute 'Event'" in str(excinfo.value)
