import pandas as pd
from src.etl.validator import validate
import sqlite3
from pathlib import Path
def test_validator_output_schema(tmp_path):
    c=sqlite3.connect(':memory:'); c.executescript(Path('src/etl/schema.sql').read_text()); c.execute("INSERT INTO companies(company_id,company_name) VALUES('TCS','TCS')"); c.commit(); out=validate(c); assert list(out.columns)==['rule_id','company_id','field','issue','severity']
