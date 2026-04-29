import pytest
from unittest.mock import MagicMock
from sync_mail.db.introspect import describe_table
from sync_mail.reconciliation.auto_yaml import generate_mapping, save_mapping_to_yaml
from sync_mail.config.schema import MappingDocument, ColumnMapping
import os

@pytest.fixture
def mock_conn():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor

def test_describe_table_success(mock_conn):
    conn, cursor = mock_conn
    cursor.fetchall.return_value = [
        {'COLUMN_NAME': 'id', 'DATA_TYPE': 'int', 'COLUMN_TYPE': 'int(11)', 'IS_NULLABLE': 'NO', 'COLUMN_DEFAULT': None, 'EXTRA': 'auto_increment', 'ORDINAL_POSITION': 1}
    ]
    
    result = describe_table(conn, 'test_db', 'test_table')
    
    assert len(result) == 1
    assert result[0]['COLUMN_NAME'] == 'id'
    cursor.execute.assert_called_once()

def test_generate_mapping_scenarios():
    source_meta = [
        {'COLUMN_NAME': 'id', 'DATA_TYPE': 'int', 'COLUMN_TYPE': 'int(11)'},
        {'COLUMN_NAME': 'status', 'DATA_TYPE': 'enum', 'COLUMN_TYPE': "enum('active','inactive')"},
        {'COLUMN_NAME': 'deleted_col', 'DATA_TYPE': 'varchar', 'COLUMN_TYPE': 'varchar(255)'},
    ]
    target_meta = [
        {'COLUMN_NAME': 'id', 'DATA_TYPE': 'int', 'COLUMN_TYPE': 'int(11)'},
        {'COLUMN_NAME': 'status', 'DATA_TYPE': 'varchar', 'COLUMN_TYPE': 'varchar(64)'},
        {'COLUMN_NAME': 'migrated_at', 'DATA_TYPE': 'datetime', 'COLUMN_TYPE': 'datetime'},
    ]
    
    doc = generate_mapping(source_meta, target_meta, 'src_tbl', 'tgt_tbl')
    
    assert doc.source_table == 'src_tbl'
    assert doc.target_table == 'tgt_tbl'
    assert len(doc.mappings) == 3
    
    # id: NONE
    m_id = doc.mappings[0]
    assert m_id.target_column == 'id'
    assert m_id.transformation_type == 'NONE'
    
    # status: CAST
    m_status = doc.mappings[1]
    assert m_status.target_column == 'status'
    assert m_status.transformation_type == 'CAST'
    assert m_status.cast_target == 'varchar(64)'
    
    # migrated_at: INJECT_DEFAULT
    m_migrated = doc.mappings[2]
    assert m_migrated.target_column == 'migrated_at'
    assert m_migrated.transformation_type == 'INJECT_DEFAULT'
    assert m_migrated.default_value == 'ACTION_REQUIRED'
    
    # deleted_col: Unmapped
    assert 'deleted_col' in doc.unmapped_source_columns

def test_save_mapping_to_yaml(tmp_path):
    mappings_dir = tmp_path / "mappings"
    doc = MappingDocument(
        source_table='src_tbl',
        target_table='tgt_tbl',
        pk_column='id',
        mappings=[
            ColumnMapping(target_column='id', source_column='id', transformation_type='NONE', _source_type='int(11)'),
            ColumnMapping(target_column='status', source_column='status', transformation_type='CAST', cast_target='varchar(64)', _source_type="enum('a','b')", _target_type='varchar(64)'),
            ColumnMapping(target_column='migrated_at', source_column=None, transformation_type='INJECT_DEFAULT', default_value='ACTION_REQUIRED', _target_type='datetime')
        ],
        unmapped_source_columns=['deleted_col']
    )
    
    filepath = save_mapping_to_yaml(doc, output_dir=str(mappings_dir))
    
    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        content = f.read()
        assert "source_table: src_tbl" in content
        assert "CAST: enum('a','b') -> varchar(64)" in content
        assert "ACTION_REQUIRED: verify mapping" in content
        assert "# UNMAPPED SOURCE COLUMNS:" in content
        assert "# - deleted_col" in content

def test_generate_mapping_identical():
    meta = [
        {'COLUMN_NAME': 'id', 'DATA_TYPE': 'int', 'COLUMN_TYPE': 'int(11)'},
        {'COLUMN_NAME': 'name', 'DATA_TYPE': 'varchar', 'COLUMN_TYPE': 'varchar(255)'},
    ]
    
    doc = generate_mapping(meta, meta, 'tbl', 'tbl')
    
    assert len(doc.mappings) == 2
    assert all(m.transformation_type == 'NONE' for m in doc.mappings)
    assert not doc.unmapped_source_columns
