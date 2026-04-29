# src/sync_mail/db/connection.py

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

    # Required parameters with sensible defaults
    host = dsn_params.get("host", "localhost")
    port = int(dsn_params.get("port", 3306))
    user = dsn_params.get("user")
    password = dsn_params.get("password")
    database = dsn_params.get("database")

    # Connection arguments
    # SSDictCursor is mandatory for low-memory footprint (server-side cursor)
    connect_args = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.SSDictCursor,
        "autocommit": False,
        # SET SESSION sql_log_off=1 to disable query logging on server side if privileges allow.
        "init_command": "SET SESSION sql_log_off=1",
    }

    try:
        conn = pymysql.connect(**connect_args)
        logger.debug(f"Established {role} database connection to {host}:{port}/{database}")
        return conn
    except pymysql.MySQLError as e:
        context = {
            "role": role,
            "host": host,
            "port": port,
            "database": database,
        }
        # Wrap into domain exception
        raise ConnectionError(f"Failed to connect to {role} database: {str(e)}", context=context) from e

@contextmanager
def connection_scope(role: str, dsn_params: Dict[str, Any]) -> Generator[pymysql.connections.Connection, None, None]:
    """
    Context manager to ensure database connection is closed properly.
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
    Context manager for atomic transactions on the database.
    """
    try:
        # Explicitly start a transaction if needed, though autocommit=False already does this.
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
        yield
        conn.commit()
        logger.debug("Transaction committed.")
    except Exception:
        conn.rollback()
        logger.debug("Transaction rolled back.")
        raise

def create_db_engine(dsn_params: Dict[str, Any]) -> Engine:
    """
    Creates a SQLAlchemy engine configured for MariaDB with server-side cursors.
    Useful for introspection and other SQLAlchemy-based tasks.
    """
    user = dsn_params.get("user")
    password = dsn_params.get("password")
    host = dsn_params.get("host", "localhost")
    port = dsn_params.get("port", 3306)
    database = dsn_params.get("database")

    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    engine = create_engine(
        db_url,
        poolclass=NullPool,
        connect_args={
            "cursorclass": pymysql.cursors.SSDictCursor,
            "autocommit": False,
            "init_command": "SET SESSION sql_log_off=1"
        },
        echo=False
    )
    return engine
