"""
Database connection and initialization for MySQL.
"""
import os
import mysql.connector
from mysql.connector import pooling

_pool = None


def _get_pool():
    """Get or create the connection pool."""
    global _pool
    if _pool is None:
        # First, create the database if it doesn't exist
        _ensure_database_exists()
        _pool = pooling.MySQLConnectionPool(
            pool_name="financial_pool",
            pool_size=5,
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "financial_copilot"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
        )
    return _pool


def _ensure_database_exists():
    """Create the database if it doesn't exist."""
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        port=int(os.getenv("MYSQL_PORT", "3306")),
    )
    cursor = conn.cursor()
    db_name = os.getenv("MYSQL_DATABASE", "financial_copilot")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cursor.close()
    conn.close()


def get_connection():
    """Get a connection from the pool."""
    return _get_pool().get_connection()


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(500) NOT NULL,
            upload_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            year VARCHAR(50),
            revenue DECIMAL(20, 2),
            profit DECIMAL(20, 2),
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            revenue_growth DECIMAL(10, 2),
            profit_margin DECIMAL(10, 2),
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] Database initialized successfully")
