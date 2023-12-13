import os
import sqlite3
import pytest
from pathlib import Path
from modules.sqldb import create_db

wd = Path().resolve()
db_file = 'test.db'
db_path = wd / db_file
if os.path.isfile(db_path):
    os.remove(db_path)

# # random_telegram_fields = set([str(randint(1, 99)).zfill(2) for i in range(20)])
# print(random_telegram_fields)


@pytest.fixture()
def create_db_():
    create_db(dbpath=db_file)


def test_db_schema(create_db_):
    con = sqlite3.connect(str(db_file))
    cur = con.cursor()
    table_info = cur.execute("PRAGMA table_info('disdrodl');")
    table_info_res = table_info.fetchall()
    table_cols = ['id', 'timestamp', 'datetime', 'parsivel_id', 'telegram']
    table_cols_dt = ['INTEGER', 'REAL', 'TEXT', 'TEXT', 'TEXT']
    for i, col in enumerate(table_info_res):
        print(col)
        assert col[1] == table_cols[i]
        assert col[2] == table_cols_dt[i]

# TODO: insert data to  db


# def test_db_select(create_db_):
#     engine = create_engine(f'sqlite:///{db_file}', echo=False)
#     with engine.connect() as conn:
#         rs = conn.execute(text('SELECT * FROM disdrodl'))
#         # import pdb; pdb.set_trace()
#         rs.rowcount
#         rs.first()

        # for i, rs_item in enumerate(rs):
        #     print(i, rs_item)
