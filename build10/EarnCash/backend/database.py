"""
Database connection helper.
Provides a small context manager so routes never forget to close
connections/cursors, and errors don't leak raw driver exceptions.
"""

from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error
from config import Config

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="earncash_pool",
            pool_size=10,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=False,
        )
    return _pool


@contextmanager
def get_db():
    """
    Usage:
        with get_db() as (conn, cursor):
            cursor.execute(...)
            conn.commit()
    Rolls back automatically if an exception is raised, and always
    closes the cursor/connection (connection returns to the pool).
    """
    conn = None
    cursor = None
    try:
        conn = _get_pool().get_connection()
        cursor = conn.cursor(dictionary=True)
        yield conn, cursor
    except Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
