import sqlite3
from pathlib import Path
from src.common import DB_PATH, OUTPUT_DIR, REPORT_DIR

def test_db_exists(): assert DB_PATH.exists()
def test_companies_92(): assert sqlite3.connect(DB_PATH).execute('select count(*) from companies').fetchone()[0]==92
def test_fk_clean(): assert list(sqlite3.connect(DB_PATH).execute('pragma foreign_key_check'))==[]
def test_ratios_1100(): assert sqlite3.connect(DB_PATH).execute('select count(*) from financial_ratios').fetchone()[0]>=1100
