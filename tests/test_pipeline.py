# tests/test_pipeline.py

import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, UTC
from sync_mail.pipeline.extractor import extract
from sync_mail.pipeline.transformer import transform
from sync_mail.pipeline.loader import Loader, load
from sync_mail.config.schema import MappingDocument, ColumnMapping
from sync_mail.errors import BatchFailedError

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.mapping = MappingDocument(
            source_table="src_table",
            target_table="tgt_table",
            pk_column="id",
            batch_size=10,
            mappings=[
                ColumnMapping(target_column="id", transformation_type="NONE", source_column="id"),
                ColumnMapping(target_column="name", transformation_type="NONE", source_column="source_name"),
                ColumnMapping(target_column="age", transformation_type="CAST", source_column="source_age", cast_target="INTEGER"),
                ColumnMapping(target_column="score", transformation_type="CAST", source_column="source_score", cast_target="DECIMAL"),
                ColumnMapping(target_column="status", transformation_type="CAST", source_column="source_status", cast_target="VARCHAR"),
                ColumnMapping(target_column="created_at", transformation_type="INJECT_DEFAULT", default_value="CURRENT_TIMESTAMP"),
                ColumnMapping(target_column="sync_version", transformation_type="INJECT_DEFAULT", default_value="v1")
            ]
        )

    def test_transformer_success(self):
        rows = [
            {"id": 1, "source_name": "Alice", "source_age": "25", "source_score": "95.5", "source_status": "ACTIVE"},
            {"id": 2, "source_name": "Bob", "source_age": 30, "source_score": 88, "source_status": "PENDING"}
        ]
        
        transformed = transform(rows, self.mapping)
        
        self.assertEqual(len(transformed), 2)
        
        # Row 1
        # Order: id, name, age, score, status, created_at, sync_version
        self.assertEqual(transformed[0][0], 1)
        self.assertEqual(transformed[0][1], "Alice")
        self.assertEqual(transformed[0][2], 25)
        self.assertEqual(transformed[0][3], Decimal("95.5"))
        self.assertEqual(transformed[0][4], "ACTIVE")
        self.assertIsInstance(transformed[0][5], datetime)
        self.assertEqual(transformed[0][6], "v1")
        
        # Row 2
        self.assertEqual(transformed[1][0], 2)
        self.assertEqual(transformed[1][2], 30)
        self.assertEqual(transformed[1][3], Decimal("88"))

    def test_transformer_cast_fail(self):
        rows = [{"id": 1, "source_name": "Alice", "source_age": "not-a-number"}]
        with self.assertRaises(BatchFailedError) as cm:
            transform(rows, self.mapping)
        self.assertIn("Transformation CAST failed", str(cm.exception))

    @patch("sync_mail.pipeline.loader.transaction")
    def test_loader_success(self, mock_transaction):
        conn = MagicMock()
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.rowcount = 2
        
        transformed_rows = [
            (1, "Alice", 25, Decimal("95.5"), "ACTIVE", datetime.now(), "v1"),
            (2, "Bob", 30, Decimal("88.0"), "PENDING", datetime.now(), "v1")
        ]
        
        loader = Loader(self.mapping)
        count = loader.load(conn, transformed_rows)
        
        self.assertEqual(count, 2)
        self.assertTrue(cursor.executemany.called)
        sql = cursor.executemany.call_args[0][0]
        self.assertIn("INSERT INTO `tgt_table`", sql)
        self.assertIn("`id`, `name`, `age`, `score`, `status`, `created_at`, `sync_version`", sql)

    @patch("sync_mail.pipeline.loader.transaction")
    def test_loader_fail(self, mock_transaction):
        conn = MagicMock()
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.executemany.side_effect = Exception("DB Error")
        
        transformed_rows = [(1, "Alice", 25, Decimal("95.5"), "ACTIVE", datetime.now(), "v1")]
        
        with self.assertRaises(BatchFailedError):
            load(conn, self.mapping, transformed_rows)

    def test_extractor_generator(self):
        conn = MagicMock()
        cursor = conn.cursor.return_value.__enter__.return_value
        
        # Mock fetchall to return a batch then empty
        cursor.fetchall.side_effect = [
            [{"id": 1, "source_name": "A"}, {"id": 2, "source_name": "B"}],
            []
        ]
        
        gen = extract(conn, self.mapping, 0)
        batch = next(gen)
        
        self.assertEqual(len(batch), 2)
        self.assertEqual(batch[0]["id"], 1)
        
        with self.assertRaises(StopIteration):
            next(gen)
            
        # Verify SQL
        sql = cursor.execute.call_args[0][0]
        self.assertIn("SELECT", sql)
        self.assertIn("FROM `src_table`", sql)
        self.assertIn("WHERE `id` > %s", sql)
        self.assertIn("ORDER BY `id` ASC", sql)
        self.assertIn("LIMIT %s", sql)

if __name__ == "__main__":
    unittest.main()
