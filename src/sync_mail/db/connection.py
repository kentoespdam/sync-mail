import pymysql
import pymysql.cursors
from contextlib import contextmanager
from typing import Dict, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from sync_mail.errors import ConnectionError
from sync_mail.observability import logger

def connect(role: str, dsn_params: Dict[str, Any]) -> pymysql.connections.Connection:
    """
    Establishes a low-memory MariaDB connection using SSDictCursor.
    
    Args:
        role (str): 'source' or 'target'
        dsn_params (Dict[str, Any]): Connection parameters (host, port, user, password, database)
        
    Returns:
        pymysql.connections.Connection: A raw PyMySQL connection object.
    """
    if role not in ["source", "target"]:
        raise ValueError(f"Invalid role: {role}. Must be 'source' or 'target'.")

    host = dsn_params.get("host", "localhost")
    port = int(dsn_params.get("port", 3306))
    user = dsn_params.get("user")
    password = dsn_params.get("password")
    database = dsn_params.get("database")

    connect_args = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.SSDictCursor, # Server-side cursor for low memory
        "autocommit": False,
        # Try to disable session logging to avoid SQL exposure in server logs
        "init_command": "SET SESSION sql_log_off=1",
    }

    try:
        conn = pymysql.connect(**connect_args)
        logger.debug(f"Connected to {role} database ({host}:{port}/{database})")
        return conn
    except pymysql.MySQLError as e:
        context = {
            "role": role,
            "host": host,
            "port": port,
            "database": database,
        }
        raise ConnectionError(f"Failed to connect to {role} database: {str(e)}", context=context) from e

@contextmanager
def connection_scope(role: str, dsn_params: Dict[str, Any]) -> Generator[pymysql.connections.Connection, None, None]:
    """
    Context manager for database connection lifecycle.
    """
    conn = connect(role, dsn_params)
    try:
        yield conn
    finally:
        conn.close()
        logger.debug(f"Closed {role} database connection.")

@contextmanager
def transaction(conn: pymysql.connections.Connection) -> Generator[None, None, None]:
    """
    Context manager for atomic transactions.
    Ensures BEGIN is sent at start, COMMIT on success, and ROLLBACK on error.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def create_db_engine(dsn_params: Dict[str, Any]) -> Engine:
    """
    Creates a SQLAlchemy engine for introspection with low-memory settings.
    """
    user = dsn_params.get("user")
    password = dsn_params.get("password")
    host = dsn_params.get("host", "localhost")
    port = dsn_params.get("port", 3306)
    database = dsn_params.get("database")

    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    return create_engine(
        db_url,
        poolclass=NullPool,
        connect_args={
            "cursorclass": pymysql.cursors.SSDictCursor,
            "autocommit": False,
            "init_command": "SET SESSION sql_log_off=1"
        },
        echo=False
    )
