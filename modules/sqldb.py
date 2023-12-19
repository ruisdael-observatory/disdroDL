from ctypes import Union
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


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def sql_query_gen(con, query):
    con.row_factory = dict_factory
    for row in con.execute(query):
        yield row
