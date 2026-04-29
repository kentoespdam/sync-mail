import pytest
import os
from sync_mail.config.loader import load_mapping
from sync_mail.errors.exceptions import MappingError

@pytest.fixture
def temp_yaml(tmp_path):
    def _create(content):
        p = tmp_path / "mapping.yaml"
        p.write_text(content)
        return str(p)
    return _create

def test_load_valid_mapping(temp_yaml):
    content = """
source_table: users_legacy
target_table: users_new
batch_size: 10000
mappings:
  - target_column: id
    source_column: old_id
    transformation_type: NONE
  - target_column: email
    source_column: email
    transformation_type: NONE
"""
    doc = load_mapping(temp_yaml(content))
    assert doc.source_table == "users_legacy"
    assert doc.target_table == "users_new"
    assert len(doc.mappings) == 2

def test_load_invalid_batch_size(temp_yaml):
    content = """
source_table: src
target_table: tgt
batch_size: 100
mappings:
  - target_column: id
    source_column: id
"""
    with pytest.raises(MappingError) as exc:
        load_mapping(temp_yaml(content))
    assert "batch_size" in str(exc.value)
    assert "5.000 - 15.000" in str(exc.value)

def test_load_missing_cast_target(temp_yaml):
    content = """
source_table: src
target_table: tgt
mappings:
  - target_column: status
    source_column: status
    transformation_type: CAST
"""
    with pytest.raises(MappingError) as exc:
        load_mapping(temp_yaml(content))
    assert "CAST" in str(exc.value)
    assert "cast_target" in str(exc.value)

def test_load_action_required_remaining(temp_yaml):
    content = """
source_table: src
target_table: tgt
mappings:
  - target_column: created_at
    source_column: None
    transformation_type: INJECT_DEFAULT
    default_value: ACTION_REQUIRED
"""
    with pytest.raises(MappingError) as exc:
        load_mapping(temp_yaml(content))
    assert "ACTION_REQUIRED" in str(exc.value)

def test_load_duplicate_target(temp_yaml):
    content = """
source_table: src
target_table: tgt
mappings:
  - target_column: email
    source_column: email1
  - target_column: email
    source_column: email2
"""
    with pytest.raises(MappingError) as exc:
        load_mapping(temp_yaml(content))
    assert "Duplikasi target_column" in str(exc.value)
    assert "email" in str(exc.value)

def test_aggregate_errors(temp_yaml):
    content = """
source_table: ""
target_table: tgt
batch_size: 1
mappings:
  - target_column: col1
    transformation_type: CAST
"""
    with pytest.raises(MappingError) as exc:
        load_mapping(temp_yaml(content))
    
    error_msg = str(exc.value)
    assert "source_table" in error_msg
    assert "batch_size" in error_msg
    assert "CAST" in error_msg
    assert error_msg.count("-") >= 3 # Multiple errors

def test_error_line_numbers(temp_yaml):
    content = """source_table: src
target_table: tgt
mappings:
  - target_column: col1
    transformation_type: CAST
"""
    # CAST error should be on line 4 (index 3 in mappings list)
    # Wait, the mappings list starts on line 3.
    # - target_column is on line 4.
    with pytest.raises(MappingError) as exc:
        load_mapping(temp_yaml(content))
    
    assert "Baris 4:" in str(exc.value)
