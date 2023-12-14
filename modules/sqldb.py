import sqlite3
from typing import Tuple
# telegram_fields = config_dict['telegram_fields'].keys()


def connect_db(dbpath: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(dbpath)
    cur = con.cursor()
    return con, cur


def create_db(dbpath):
    '''
    create disdrodl.db
    with Table: disdrodl 
    with columns id, timestamp, parsivel_id, telegram 
    '''  
    con, cur = connect_db(dbpath=str(dbpath))
    cur.execute("""
                CREATE TABLE IF NOT EXISTS disdrodl
                (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    datetime TEXT,
                    parsivel_id TEXT,
                    telegram TEXT
                )
                """)
    con.commit()
    return con, cur