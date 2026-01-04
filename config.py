import sqlite3
import os
from pathlib import Path

class DatabaseConfig:
    # SQLite configuration
    DB_NAME = "student_management.db"
    DB_PATH = Path(__file__).parent / DB_NAME
    
    @staticmethod
    def get_connection():
        try:
            conn = sqlite3.connect(DatabaseConfig.DB_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            print("✅ Database connected successfully")
            return conn
        except Exception as e:
            print(f"❌ Error connecting to SQLite: {e}")
            return None
