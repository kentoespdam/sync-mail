import pytest
from decimal import Decimal
from sync_mail.pipeline.transformer import transform
from sync_mail.config.schema import MappingDocument, ColumnMapping

def test_transform_none():
    mapping = MappingDocument(
        source_table="s", target_table="t", pk_column="id",
        mappings=[ColumnMapping(target_column="name", source_column="name", transformation_type="NONE")]
    )
    rows = [{"id": 1, "name": "Alice"}]
    result = transform(rows, mapping)
    assert result == [("Alice",)]

def test_transform_cast():
    mapping = MappingDocument(
        source_table="s", target_table="t", pk_column="id",
        mappings=[
            ColumnMapping(target_column="age", source_column="age_str", transformation_type="CAST", cast_target="INTEGER"),
            ColumnMapping(target_column="price", source_column="price_str", transformation_type="CAST", cast_target="DECIMAL")
        ]
    )
    rows = [{"id": 1, "age_str": "25", "price_str": "10.99"}]
    result = transform(rows, mapping)
    assert result == [(25, Decimal("10.99"))]

def test_transform_inject_default():
    mapping = MappingDocument(
        source_table="s", target_table="t", pk_column="id",
        mappings=[
            ColumnMapping(target_column="const", transformation_type="INJECT_DEFAULT", default_value="FixedValue")
        ]
    )
    rows = [{"id": 1}]
    result = transform(rows, mapping)
    assert result == [("FixedValue",)]

def test_transform_current_timestamp():
    mapping = MappingDocument(
        source_table="s", target_table="t", pk_column="id",
        mappings=[
            ColumnMapping(target_column="ts", transformation_type="INJECT_DEFAULT", default_value="CURRENT_TIMESTAMP")
        ]
    )
    rows = [{"id": 1}, {"id": 2}]
    result = transform(rows, mapping)
    assert len(result) == 2
    # Ensure both rows in the same batch have the EXACT same timestamp
    assert result[0][0] == result[1][0]
    assert result[0][0] is not None

def test_transform_cast_failure():
    mapping = MappingDocument(
        source_table="s", target_table="t", pk_column="id",
        mappings=[
            ColumnMapping(target_column="age", source_column="age_str", transformation_type="CAST", cast_target="INTEGER")
        ]
    )
    rows = [{"id": 1, "age_str": "invalid"}]
    from sync_mail.errors import BatchFailedError
    with pytest.raises(BatchFailedError) as exc:
        transform(rows, mapping)
    assert "Transformation CAST failed" in str(exc.value)
