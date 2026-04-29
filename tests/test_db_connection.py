# tests/test_db_connection.py

import unittest
from unittest.mock import patch, MagicMock
import pymysql
import pymysql.cursors
from sync_mail.db.connection import connect, connection_scope, transaction
from sync_mail.errors import ConnectionError

class TestDBConnection(unittest.TestCase):
    
    def setUp(self):
        self.dsn_params = {
            "host": "localhost",
            "port": 3306,
            "user": "test_user",
            "password": "test_password",
            "database": "test_db"
        }

    @patch("pymysql.connect")
    def test_connect_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        conn = connect("source", self.dsn_params)
        
        self.assertEqual(conn, mock_conn)
        mock_connect.assert_called_once_with(
            host="localhost",
            port=3306,
            user="test_user",
            password="test_password",
            database="test_db",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.SSDictCursor,
            autocommit=False,
            init_command="SET SESSION sql_log_off=1"
        )

    @patch("pymysql.connect")
    def test_connect_failure_wraps_exception(self, mock_connect):
        mock_connect.side_effect = pymysql.MySQLError("Connection refused")
        
        with self.assertRaises(ConnectionError) as cm:
            connect("target", self.dsn_params)
            
        self.assertIn("Failed to connect to target database", str(cm.exception))
        self.assertEqual(cm.exception.context["role"], "target")

    @patch("sync_mail.db.connection.connect")
    def test_connection_scope(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with connection_scope("source", self.dsn_params) as conn:
            self.assertEqual(conn, mock_conn)
            
        mock_conn.close.assert_called_once()

    def test_transaction_commit(self):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
        
        with transaction(mock_conn):
            pass
            
        mock_cursor.execute.assert_called_with("BEGIN")
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    def test_transaction_rollback_on_error(self):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
        
        with self.assertRaises(ValueError):
            with transaction(mock_conn):
                raise ValueError("Something went wrong")
                
        mock_cursor.execute.assert_called_with("BEGIN")
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()

if __name__ == "__main__":
    unittest.main()
