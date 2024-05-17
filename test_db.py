"""
test db
"""
import os
import sqlite3
import logging
from pathlib import Path
from logging import StreamHandler
from datetime import datetime, timedelta, timezone
from netCDF4 import Dataset # pylint: disable=no-name-in-module
from cftime import num2date
from pydantic.v1.utils import deep_update
import pytest

from modules.sqldb import create_db, connect_db, query_db_rows_gen
from modules.util_functions import yaml2dict, unpack_telegram_from_db
from modules.now_time import NowTime
from modules.telegram import ParsivelTelegram
from modules.netCDF import NetCDF

parsivel_lines = [b'TYP OP4A\r\n', b'01:0000.000\r\n', b'02:0000.00\r\n', b'03:00\r\n', b'04:00\r\n', b'05:   NP\r\n', b'06:   C\r\n', b'07:-9.999\r\n', b'08:20000\r\n', b'09:00043\r\n', b'10:13894\r\n', b'11:00000\r\n', b'12:021\r\n', b'13:450994\r\n', b'14:2.11.6\r\n', b'15:2.11.1\r\n', b'16:0.50\r\n', b'17:24.3\r\n', b'18:0\r\n', b'19: \r\n', b'20:10:13:21\r\n', b'21:25.05.2023\r\n', b'22:\r\n', b'23:\r\n', b'24:0000.00\r\n', b'25:000\r\n', b'26:032\r\n', b'27:022\r\n', b'28:022\r\n', b'29:000.041\r\n', b'30:00.000\r\n', b'31:0000.0\r\n', b'32:0000.00\r\n', b'34:0000.00\r\n', b'35:0000.00\r\n', b'40:20000\r\n', b'41:20000\r\n', b'50:00000000\r\n', b'51:000140\r\n', b'90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\r\n', b'91:00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;\r\n', b'93:000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;\r\n', b'94:0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;\r\n', b'95:0.00;0.00;0.00;0.00;0.00;0.00;0.00;\r\n', b'96:0000000;0000000;0000000;0000000;0000000;0000000;0000000;\r\n', b'97:;\r\n', b'98:;\r\n', b'99:;\r\n', b'\x03'] # pylint: disable=line-too-long
now = NowTime()
wd = Path().resolve()
data_dir = wd / 'sample_data'
db_file = 'test.db'
db_path = data_dir / db_file
par008_db_file = 'disdrodl_PA008.db'
par008_db_path = data_dir / par008_db_file

log_handler = StreamHandler()
logger = logging.getLogger('test-log')
logger.addHandler(log_handler)

config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV.yml')
config_dict = deep_update(config_dict, config_dict_site)

start_dt = datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
data_points_24h = 1440  # (60min * 24h)

# # random_telegram_fields = set([str(randint(1, 99)).zfill(2) for i in range(20)])
# print(random_telegram_fields)


@pytest.fixture()
def create_db_():
    """
    create db
    """
    if os.path.isfile(db_path):
        os.remove(db_path)
    create_db(dbpath=db_path)


def test_connect_db(create_db_): # pylint: disable=unused-argument,redefined-outer-name
    """
    test connect db
    :param create_db_:
    """
    con, cur = connect_db(dbpath=str(db_path))
    assert isinstance(con, sqlite3.Connection) is True
    assert isinstance(cur, sqlite3.Cursor) is True
    cur.close()
    con.close()

def test_db_schema(create_db_): # pylint: disable=unused-argument,redefined-outer-name
    """
    test db schema
    :param create_db_:
    """
    con, cur = connect_db(dbpath=str(db_path))
    table_info = cur.execute("PRAGMA table_info('disdrodl');")
    table_info_res = table_info.fetchall()
    table_cols = ['id', 'timestamp', 'datetime', 'parsivel_id', 'telegram']
    table_cols_dt = ['INTEGER', 'REAL', 'TEXT', 'TEXT', 'TEXT']
    for i, col in enumerate(table_info_res):
        print(col)
        assert col[1] == table_cols[i]
        assert col[2] == table_cols_dt[i]
    cur.close()
    con.close()


def test_db_insert(create_db_): # pylint: disable=unused-argument,redefined-outer-name
    """
    test db insert
    :param create_db_:
    """
    con, cur = connect_db(dbpath=str(db_path))
    telegram = ParsivelTelegram(config_dict=config_dict,
                                telegram_lines=parsivel_lines,
                                timestamp=now.utc,
                                db_cursor=cur,
                                telegram_data={},
                                logger=logger)
    telegram.capture_prefixes_and_data()
    # testing Telegram method prep_telegram_data4db() argument telegram.telegram_data_str
    telegram.prep_telegram_data4db()
    assert isinstance(telegram.telegram_data_str, str) is True
    assert telegram.telegram_data_str.count(';') == len(telegram.telegram_data) - 1
    assert isinstance(telegram.db_cursor, sqlite3.Cursor) is True
    # insert data to  db
    telegram.insert2db()
    con.commit()
    # query
    res = cur.execute("SELECT id, timestamp, datetime, parsivel_id, telegram FROM disdrodl")
    for i in res.fetchall():
        assert isinstance(telegram.telegram_data_str, str) is True
        id_, timestamp, datetime_, parsivel_id, telegram_str = i
        assert isinstance(id_, int) is True
        assert isinstance(timestamp, float) is True
        timestamp_as_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        assert timestamp_as_dt == now.utc
        datetime_as_dt = datetime.strptime(datetime_.split('+')[0], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        assert datetime_as_dt == now.utc
        assert timestamp_as_dt == datetime_as_dt
        assert isinstance(datetime_, str) is True
        assert parsivel_id == config_dict['global_attrs']['sensor_name']
        assert isinstance(telegram_str, str) is True
        print('test.db', timestamp, datetime_)

    res = cur.execute("SELECT COUNT(*) FROM disdrodl;")
    assert res.fetchone()[0] == 1
    cur.close()
    con.close()
    # print(telegram.telegram_lines)


def test_unpack_telegram_from_db():
    """
    test unpack telegram from db
    """
    db_row = (1, 1702542494.204936, '2023-12-14T09:28:14.204936', 'PAR008', '01:0000.000; 02:0000.00; 03:00; 04:00; 05:NP; 06:C; 07:-9.999; 08:20000; 09:00043; 10:13894; 11:00000; 12:021; 13:450994; 14:2.11.6; 15:2.11.1; 16:0.50; 17:24.3; 18:0; 19:None; 20:10; 21:25.05.2023; 22:None; 23:None; 24:0000.00; 25:000; 26:032; 27:022; 28:022; 29:000.041; 30:00.000; 31:0000.0; 32:0000.00; 34:0000.00; 35:0000.00; 40:20000; 41:20000; 50:00000000; 51:000140; 90:-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999,-9.999; 91:00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000,00.000; 93:000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000; 94:0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000,0000; 95:0.00,0.00,0.00,0.00,0.00,0.00,0.00; 96:0000000,0000000,0000000,0000000,0000000,0000000,0000000') # pylint: disable=line-too-long
    telegram_tmp_dict = unpack_telegram_from_db(telegram_str=db_row[-1])
    assert telegram_tmp_dict['01'] == '0000.000'
    assert telegram_tmp_dict['10'] == '13894'
    assert telegram_tmp_dict['95'] == '0.00,0.00,0.00,0.00,0.00,0.00,0.00'
    # print(telegram_tmp_dict)


parsivel_lines = [b'TYP OP4A\r\n', b'01:0000.000\r\n', b'02:0000.00\r\n', b'03:00\r\n', b'04:00\r\n', b'05:   NP\r\n', b'06:   C\r\n', b'07:-9.999\r\n', b'08:20000\r\n', b'09:00043\r\n', b'10:13894\r\n', b'11:00000\r\n', b'12:021\r\n', b'13:450994\r\n', b'14:2.11.6\r\n', b'15:2.11.1\r\n', b'16:0.50\r\n', b'17:24.3\r\n', b'18:0\r\n', b'19: \r\n', b'20:10:13:21\r\n', b'21:25.05.2023\r\n', b'22:\r\n', b'23:\r\n', b'24:0000.00\r\n', b'25:000\r\n', b'26:032\r\n', b'27:022\r\n', b'28:022\r\n', b'29:000.041\r\n', b'30:00.000\r\n', b'31:0000.0\r\n', b'32:0000.00\r\n', b'34:0000.00\r\n', b'35:0000.00\r\n', b'40:20000\r\n', b'41:20000\r\n', b'50:00000000\r\n', b'51:000140\r\n', b'90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\r\n', b'91:00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;\r\n', b'93:000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;\r\n', b'94:0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;\r\n', b'95:0.00;0.00;0.00;0.00;0.00;0.00;0.00;\r\n', b'96:0000000;0000000;0000000;0000000;0000000;0000000;0000000;\r\n', b'97:;\r\n', b'98:;\r\n', b'99:;\r\n', b'\x03'] # pylint: disable=line-too-long


@pytest.fixture()
def db_insert_24h(create_db_): # pylint: disable=unused-argument,redefined-outer-name
    """
    db insert 24h
    :param create_db_:
    """
    # inserts 1440 rows to db
    con, cur = connect_db(dbpath=str(db_path))
    for i in range(data_points_24h):
        new_time = start_dt + timedelta(minutes=i)  # time offset: by 1 minute
        telegram = ParsivelTelegram(config_dict=config_dict,
                                    telegram_lines=parsivel_lines,
                                    timestamp=new_time,
                                    db_cursor=cur,
                                    telegram_data={},
                                    logger=logger)
        telegram.capture_prefixes_and_data()
        telegram.prep_telegram_data4db()
        telegram.insert2db()
    con.commit()
    cur.close()
    con.close()


def test_query_db(db_insert_24h): # pylint: disable=unused-argument,redefined-outer-name
    """
    test query db
    :param db_insert_24h:
    """
    delete_netcdf(fn_start='test', data_dir=data_dir,)  # delete old netCDF
    telegram_objs = []
    con, cur = connect_db(dbpath=str(db_path))
    res = cur.execute("SELECT COUNT(*) FROM disdrodl;")
    assert res.fetchone()[0] == data_points_24h
    for i, row in enumerate(query_db_rows_gen(con=con, date_dt=start_dt, logger=logger)):
        # test time
        assert isinstance(row, dict) is True
        dt_col_val = datetime.fromisoformat(row.get('datetime'))
        calculated_dt = start_dt + timedelta(minutes=i)
        assert dt_col_val == calculated_dt
        ts_dt = datetime.fromtimestamp(row.get('timestamp'), tz=timezone.utc)
        assert ts_dt == dt_col_val
        assert ts_dt == calculated_dt
        row_telegram = ParsivelTelegram(
            config_dict=config_dict,
            telegram_lines=row.get('telegram'),
            timestamp=ts_dt,
            db_cursor=None,
            telegram_data={},
            logger=logger)
        row_telegram.parse_telegram_row()
        telegram_objs.append(row_telegram)
    cur.close()
    con.close()
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=data_dir,
                fn_start='test',
                telegram_objs=telegram_objs,
                date=start_dt)
    nc.create_netCDF()
    nc.write_data_to_netCDF()
    nc.compress()


def test_NetCDF():
    """
    test netCDF
    """
    rootgrp = Dataset(data_dir / 'test.nc', 'r', format="NETCDF4")  # read netcdf
    # test NetCDF time and datetime variables values
    netCDF_var_time = rootgrp.variables['time']
    netCDF_var_time_data = netCDF_var_time[:].data
    assert len(netCDF_var_time_data) == data_points_24h
    netCDF_var_datetime = rootgrp.variables['datetime']
    netCDF_var_datetime_data = netCDF_var_datetime[:]
    first_nc_time_val = num2date(
        netCDF_var_time_data[0],
        units=f'hours since {start_dt.strftime("%Y-%m-%d %H:%M:%S")} +00:00'
    )
    assert first_nc_time_val.strftime("%Y-%m-%dT%H:%M:%S") == netCDF_var_datetime_data[0][:-6]
    last_nc_time_val = num2date(
        netCDF_var_time_data[-1],
        units=f'hours since {start_dt.strftime("%Y-%m-%d %H:%M:%S")} +00:00'
    )
    assert last_nc_time_val.strftime("%Y-%m-%dT%H:%M:%S") == netCDF_var_datetime_data[-1][:-6]
    # test other NetCDF int & float vars
    netCDF_var_MOR = rootgrp.variables['MOR']
    netCDF_var_MOR_data = netCDF_var_MOR[:].data
    assert netCDF_var_MOR_data[0] == float(20000.0)
    netCDF_var_amp = rootgrp.variables['amplitude']
    netCDF_var_amp_data = netCDF_var_amp[:].data
    assert netCDF_var_amp_data[0] == 13894
    netCDF_var_temp_l_sensor = rootgrp.variables['T_L_sensor_head']
    netCDF_var_temp_l_sensor_data = netCDF_var_temp_l_sensor[:].data
    netCDF_var_temp_r_sensor = rootgrp.variables['T_R_sensor_head']
    netCDF_var_temp_r_sensor_data = netCDF_var_temp_r_sensor[:].data

    # same temp on L & R sensors: only valid for current data
    assert netCDF_var_temp_r_sensor_data[0] == netCDF_var_temp_l_sensor_data[0]
    # test NetCDF (F93) data_raw var - test shape is 32x32 ndarry for each data point
    netCDF_var_data_raw = rootgrp.variables['data_raw']
    netCDF_var_data_raw_data = netCDF_var_data_raw[:].data
    netCDF_var_data_raw_shape = netCDF_var_data_raw_data.shape
    # print(netCDF_var_data_raw_shape)
    assert netCDF_var_data_raw_shape == (data_points_24h, 32, 32)


def delete_netcdf(fn_start, data_dir): # pylint: disable=redefined-outer-name
    """
    delete netcdf
    :param fn_start:
    :param data_dir:
    """
    test_nc_path = data_dir / f'{fn_start}.nc'
    if os.path.exists(test_nc_path):
        os.remove(test_nc_path)


@pytest.fixture()
def db_insert_24h_w_gaps(create_db_): # pylint: disable=unused-argument,redefined-outer-name
    """
    db insert 24h with gaps
    :param create_db_:
    """
    # inserts 1440 rows to db, but in half of entries, telegram is empty
    con, cur = connect_db(dbpath=str(db_path))
    for i in range(data_points_24h):
        new_time = start_dt + timedelta(minutes=i)  # time offset: by 1 minute
        if i % 2 == 0:
            data_lines = parsivel_lines
        else:
            data_lines = []  # odd index: empty list, instead of parsivel_lines
        telegram = ParsivelTelegram(config_dict=config_dict,
                                    telegram_lines=data_lines,
                                    timestamp=new_time,
                                    db_cursor=cur,
                                    telegram_data={},
                                    logger=logger)
        telegram.capture_prefixes_and_data()
        telegram.prep_telegram_data4db()
        telegram.insert2db()
    con.commit()
    cur.close()
    con.close()


def test_NetCDF_w_gaps(db_insert_24h_w_gaps): # pylint: disable=unused-argument,redefined-outer-name
    '''
    def should test if the db rows with empty telegram data
    are not included in NetCDF
    '''
    delete_netcdf(fn_start='test', data_dir=data_dir,)  # delete old netCDF
    telegram_objs = []
    con, cur = connect_db(dbpath=str(db_path))
    returned_rows = 0
    for row in query_db_rows_gen(con=con, date_dt=start_dt, logger=logger):
        returned_rows += 1
        ts_dt = datetime.fromtimestamp(row.get('timestamp'), tz=timezone.utc)
        row_telegram = ParsivelTelegram(
            config_dict=config_dict,
            telegram_lines=row.get('telegram'),
            timestamp=ts_dt,
            db_cursor=None,
            telegram_data={},
            logger=logger)
        row_telegram.parse_telegram_row()
        if row_telegram.telegram_data.keys() and \
            '90' in row_telegram.telegram_data.keys() and \
            '91' in row_telegram.telegram_data.keys() and \
            '93' in row_telegram.telegram_data.keys():
            # append only rows w telegram data
            telegram_objs.append(row_telegram)
    cur.close()
    con.close()
    # len(telegram_objs) should be half of returned_rows,
    # as def db_insert_24h_w_gaps includes telegram data, only in half of
    # the db entries
    assert len(telegram_objs) == returned_rows / 2
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=data_dir,
                fn_start='test_w_gaps',
                telegram_objs=telegram_objs,
                date=start_dt)
    nc.create_netCDF()
    nc.write_data_to_netCDF()
    nc.compress()
    # test netCDF content
    rootgrp = Dataset(data_dir / 'test_w_gaps.nc', 'r', format="NETCDF4")
    # test NetCDF time and datetime variables values
    netCDF_var_time = rootgrp.variables['time']
    netCDF_var_time_data = netCDF_var_time[:].data
    assert len(netCDF_var_time_data) == data_points_24h / 2
    # netCDF_var_datetime = rootgrp.variables['datetime']
    # test gap between 1st and 2nd measure: 120secs
    # since 2nd db entry was skipped, due to not having data
    first_nc_time_val = num2date(
        netCDF_var_time_data[0],
        units=f'hours since {start_dt.strftime("%Y-%m-%d %H:%M:%S")} +00:00'
    )
    second_nc_time_val = num2date(
        netCDF_var_time_data[1],
        units=f'hours since {start_dt.strftime("%Y-%m-%d %H:%M:%S")} +00:00'
    )
    delta = second_nc_time_val - first_nc_time_val
    assert delta.seconds == 120
    # test NetCDF (F93) data_raw var - test shape is 32x32 ndarry for each data point
    netCDF_var_data_raw = rootgrp.variables['data_raw']
    netCDF_var_data_raw_data = netCDF_var_data_raw[:].data
    netCDF_var_data_raw_shape = netCDF_var_data_raw_data.shape
    assert netCDF_var_data_raw_shape == (data_points_24h / 2, 32, 32)
