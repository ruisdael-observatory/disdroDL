"""
This module contains functionalities to use with the sql database.

Functions:
- connect_db: Connects to the database at the given path.
- create_db: Creates disdrodl.db if it does not exist yet.
- dict_factory: TBD
- sql_query_gen: TBD
- query_db_rows_gen: Queries the row for the given date.
"""

import sqlite3
from typing import Tuple
from datetime import timezone
# telegram_fields = config_dict['telegram_fields'].keys()


def connect_db(dbpath: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    '''
    Sets up a connection with the database at the path provided as argument.
    '''
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
    '''
    TBD
    '''
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)} # pylint: disable=unnecessary-comprehension


def sql_query_gen(con, query):
    '''
    TBD
    '''
    con.row_factory = dict_factory
    yield from con.execute(query)


def query_db_rows_gen(con, date_dt, logger):
    '''
    Query db: entries for the date_dt (year,month,day)
    between 00:00:00 and 23:59:59
    Returning a row_factory generator
    '''
    start_dt = date_dt.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)  # redundant replace
    start_ts = start_dt.timestamp()
    end_dt = date_dt.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
    end_ts = end_dt.timestamp()
    query_str = f"SELECT * FROM disdrodl WHERE timestamp >= {start_ts} AND timestamp < {end_ts}"
    logger.debug(msg=query_str)
    # Append each SQL response row as Telegram instance to telegram_objs var
    con.row_factory = dict_factory
    yield from con.execute(query_str)
