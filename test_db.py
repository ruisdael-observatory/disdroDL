import pytest
import os
from pathlib import Path
from random import randint
from sqlalchemy import create_engine, inspect
from sqlalchemy import text
from modules.sqldb import create_db

wd = Path().resolve()
db_file = 'test.db'
db_path = wd / db_file
if os.path.isfile(db_path):
    os.remove(db_path)

random_telegram_fields = set([str(randint(1, 99)).zfill(2) for i in range(20)])
print(random_telegram_fields)


@pytest.fixture()
def create_db_():
    create_db(dbpath=db_file, telegram_fields=random_telegram_fields)


def test_db_schema(create_db_):
    engine = create_engine(f'sqlite:///{db_file}', echo=False)
    with engine.connect() as conn:
        inspector = inspect(engine)
        for i, col in enumerate(inspector.get_columns('disdrodl')):
            if i < len(random_telegram_fields):
                assert col['name'] == f'f_{list(random_telegram_fields)[i]}'
            elif i == len(random_telegram_fields):
                assert col['name'] == 'id'
            elif i == len(random_telegram_fields)+1:
                assert col['name'] == 'timestamp'
            elif i == len(random_telegram_fields)+2:
                assert col['name'] == 'datetime'
            elif i == len(random_telegram_fields)+3:
                assert col['name'] == 'parsivel_id'

# TODO: insert data to  db


def test_db_select(create_db_):
    engine = create_engine(f'sqlite:///{db_file}', echo=False)
    with engine.connect() as conn:
        rs = conn.execute(text('SELECT * FROM disdrodl'))
        # import pdb; pdb.set_trace()
        rs.rowcount
        rs.first()

        # for i, rs_item in enumerate(rs):
        #     print(i, rs_item)
