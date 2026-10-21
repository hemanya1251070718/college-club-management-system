import os
import pymysql
from pymysql.cursors import DictCursor
from app.config import Config

def get_db_connection():
    """
    Creates and returns a connection to MySQL.
    Connects via Unix socket if INSTANCE_CONNECTION_NAME is set (Cloud Run),
    otherwise connects via TCP (local development or proxy).
    """
    db_config = {
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "database": Config.DB_NAME,
        "cursorclass": DictCursor,
        "autocommit": True,
        "connect_timeout": 5,
    }

    if Config.INSTANCE_CONNECTION_NAME:
        # Cloud Run connects to Cloud SQL via unix socket mount
        socket_path = f"{Config.DB_SOCKET_DIR}/{Config.INSTANCE_CONNECTION_NAME}"
        db_config["unix_socket"] = socket_path
    else:
        # Local development via TCP
        db_config["host"] = Config.DB_HOST
        db_config["port"] = Config.DB_PORT

    return pymysql.connect(**db_config)

def check_db_health():
    """
    Executes a simple ping query to verify database reachability.
    Returns (status_bool, message_str, details_dict).
    """
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS healthy, VERSION() AS db_version, DATABASE() AS current_db;")
                row = cursor.fetchone()
                return True, "Database connection healthy", {
                    "version": row.get("db_version"),
                    "database": row.get("current_db"),
                    "mode": "Cloud SQL Unix Socket" if Config.INSTANCE_CONNECTION_NAME else "Local TCP",
                }
        finally:
            conn.close()
    except Exception as e:
        return False, f"Database connection error: {str(e)}", {
            "mode": "Cloud SQL Unix Socket" if Config.INSTANCE_CONNECTION_NAME else "Local TCP",
        }
