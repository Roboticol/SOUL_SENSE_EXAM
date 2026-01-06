import sqlite3
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "soulsense_db")
print("USING DB:", DB_PATH)
def get_connection(db_path: str | None = None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    return conn
