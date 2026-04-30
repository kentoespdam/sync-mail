import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sync_mail.pipeline.dry_run import DryRunEngine
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.db.target_probe import ColumnMetadata
from sync_mail.pipeline.anomaly import AnomalyCategory, AnomalySeverity

@pytest.fixture
def mock_mapping():
    return MappingDocument(
        source_table="source_table",
        target_table="target_table",
        pk_column="id",
        batch_size=10,
        mappings=[
            ColumnMapping(source_column="name", target_column="name", transformation_type="NONE"),
            ColumnMapping(source_column="age", target_column="age", transformation_type="CAST", cast_target="INTEGER")
        ]
    )

@pytest.fixture
def mock_metadata():
    return {
        "name": ColumnMetadata(
            name="name",
            data_type="VARCHAR",
            is_nullable=True,
            default=None,
            max_length=10,
            enum_values=None,
            column_type="varchar(10)"
        ),
        "age": ColumnMetadata(
            name="age",
            data_type="INT",
            is_nullable=False,
            default=None,
            max_length=None,
            enum_values=None,
            column_type="int(11)"
        )
    }

def test_dry_run_truncation(mock_mapping, mock_metadata):
    conn_source = MagicMock()
    conn_target = MagicMock()
    
    # Mock extraction: one row with a long name
    mock_cursor = conn_source.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.side_effect = [
        [{"id": 1, "name": "A very long name indeed", "age": 25}],
        [] # End of stream
    ]
    
    with patch("sync_mail.pipeline.dry_run.describe_target_columns", return_value=mock_metadata):
        engine = DryRunEngine(conn_source, conn_target, "test_schema", mock_mapping, sample_limit=10)
        report = engine.execute()
        
        assert report.status == "WARN"
        assert len(report.anomalies) == 1
        assert report.anomalies[0].category == AnomalyCategory.DATA_TRUNCATION
        assert "VARCHAR(10)" in report.anomalies[0].message
        assert "minimal 23" in report.anomalies[0].recommendation

def test_dry_run_not_null_violation(mock_mapping, mock_metadata):
    conn_source = MagicMock()
    conn_target = MagicMock()
    
    # Mock extraction: age is NULL but target is NOT NULL
    mock_cursor = conn_source.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.side_effect = [
        [{"id": 1, "name": "John", "age": None}],
        []
    ]
    
    with patch("sync_mail.pipeline.dry_run.describe_target_columns", return_value=mock_metadata):
        engine = DryRunEngine(conn_source, conn_target, "test_schema", mock_mapping, sample_limit=10)
        report = engine.execute()
        
        assert report.status == "FAIL"
        assert any(a.category == AnomalyCategory.NOT_NULL_VIOLATION for a in report.anomalies)

def test_dry_run_type_mismatch(mock_mapping, mock_metadata):
    conn_source = MagicMock()
    conn_target = MagicMock()
    
    # Mock extraction: age is 'invalid' (string)
    mock_cursor = conn_source.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.side_effect = [
        [{"id": 1, "name": "John", "age": "invalid"}],
        []
    ]
    
    with patch("sync_mail.pipeline.dry_run.describe_target_columns", return_value=mock_metadata):
        engine = DryRunEngine(conn_source, conn_target, "test_schema", mock_mapping, sample_limit=10)
        report = engine.execute()
        
        # This should trigger a TRANSFORM_ERROR because CAST will fail
        assert report.status == "FAIL"
        assert any(a.category == AnomalyCategory.TRANSFORM_ERROR for a in report.anomalies)

def test_dry_run_sample_limit(mock_mapping, mock_metadata):
    conn_source = MagicMock()
    conn_target = MagicMock()
    
    # Provide 5 rows
    rows = [{"id": i, "name": f"name_{i}", "age": i} for i in range(1, 6)]
    mock_cursor = conn_source.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.side_effect = [rows, []]
    
    with patch("sync_mail.pipeline.dry_run.describe_target_columns", return_value=mock_metadata):
        # Set limit to 3
        engine = DryRunEngine(conn_source, conn_target, "test_schema", mock_mapping, sample_limit=3)
        report = engine.execute()
        
        assert report.rows_extracted == 3
        # Ensure the extractor was called with the correct limit
        # The first call to fetchall returned 5, but we expect only 3 to be processed by engine
        # and extractor should have been called with limit 3 if total_yielded logic is correct.
        
        # Let's verify how many rows extractor yielded if we can
