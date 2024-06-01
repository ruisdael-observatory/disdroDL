"""
Module with all test fixtures.
When a test fixtures is set as argument for a test function, it automatically runs at the start of the test.

Functions:
- create_db_parsivel: Creates test_parsivel.db in sample_data if it does not exist yet.
- create_db_thies: Creates test_thies.db in sample_data if it does not exist yet.
- create_db_: Creates a database at the given path if it does not exist yet.
- db_insert_24h_parsivel: Inserts 24 hours worth of Parsivel telegrams into the test database.
- db_insert_24h_thies: Inserts 24 hours worth of Thies telegrams into the test database.
- db_insert_24h: Inserts 24 hours worth of telegrams into a test database.
- db_insert_24h_w_gaps_parsivel: Inserts 24 hours worth of Parsivel telegrams into the test database,
    but with some missing rows.
- db_insert_24h_w_gaps_thies: Inserts 24 hours worth of Thies telegrams into the test database,
    but with some missing rows.
- db_insert_24h_w_gaps: Inserts 24 hours worth of data into the test database, but with some missing rows.
- db_insert_24h_empty_parsivel: Inserts 24 hours worth of empty Telegram telegrams into the test database.
- db_insert_24h_empty_thies: Inserts 24 hours worth of empty Thies telegrams into the test database.
- db_insert_24h_empty: Inserts 24 hours worth of empty lines into a test database.
"""

import os
import logging
from pathlib import Path
from logging import StreamHandler
from datetime import datetime, timedelta, timezone
from pydantic.v1.utils import deep_update
import pytest

from modules.sqldb import create_db, connect_db
from modules.util_functions import yaml2dict
from modules.now_time import NowTime
from modules.telegram import create_telegram

# General variables

now = NowTime()
wd = Path().resolve()
data_dir = wd / 'sample_data'

log_handler = StreamHandler()
logger = logging.getLogger('test-log')
logger.addHandler(log_handler)

start_dt = datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
data_points_24h = 1440  # (60min * 24h)

# Parsivel specific variables

db_file = 'test_parsivel.db'
db_path_parsivel = data_dir / db_file

config_dict_general = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV.yml')
config_dict_parsivel = deep_update(config_dict_general, config_dict_site)

parsivel_lines = [b'TYP OP4A\r\n', b'01:0000.000\r\n', b'02:0000.00\r\n', b'03:00\r\n', b'04:00\r\n', b'05:   NP\r\n', b'06:   C\r\n', b'07:-9.999\r\n', b'08:20000\r\n', b'09:00043\r\n', b'10:13894\r\n', b'11:00000\r\n', b'12:021\r\n', b'13:450994\r\n', b'14:2.11.6\r\n', b'15:2.11.1\r\n', b'16:0.50\r\n', b'17:24.3\r\n', b'18:0\r\n', b'19: \r\n', b'20:10:13:21\r\n', b'21:25.05.2023\r\n', b'22:\r\n', b'23:\r\n', b'24:0000.00\r\n', b'25:000\r\n', b'26:032\r\n', b'27:022\r\n', b'28:022\r\n', b'29:000.041\r\n', b'30:00.000\r\n', b'31:0000.0\r\n', b'32:0000.00\r\n', b'34:0000.00\r\n', b'35:0000.00\r\n', b'40:20000\r\n', b'41:20000\r\n', b'50:00000000\r\n', b'51:000140\r\n', b'90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\r\n', b'91:00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;\r\n', b'93:000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;\r\n', b'94:0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;\r\n', b'95:0.00;0.00;0.00;0.00;0.00;0.00;0.00;\r\n', b'96:0000000;0000000;0000000;0000000;0000000;0000000;0000000;\r\n', b'97:;\r\n', b'98:;\r\n', b'99:;\r\n', b'\x03'] # pylint: disable=line-too-long

# Thies specific variables

db_file = 'test_thies.db'
db_path_thies = data_dir / db_file

config_dict_general = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_thies.yml')
config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV_THIES.yml')
config_dict_thies = deep_update(config_dict_general, config_dict_site)

thies_lines = '06;0854;2.11;01.01.14;18:59:00;00;00;NP   ;000.000;00;00;NP   ;000.000;000.000;000.000;0000.00;99999;-9.9;100;0.0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;+23;26;1662;4011;2886;258;062;063;+20.3;999;9999;9999;9999;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;99999;99999;9999;999;E9;' # pylint: disable=line-too-long
#thies_lines = '1:; 2:06; 3:0854; 4:2.11; 5:20.01.14; 6:00:00:02; 7:00; 8:00; 9:NP   ; 10:000.000; 11:00; 12:00; 13:NP   ; 14:000.000; 15:000.000; 16:000.000; 17:0125.07; 18:99999; 19:-9.9; 20:100; 21:0.0; 22:0; 23:0; 24:0; 25:0; 26:0; 27:0; 28:0; 29:0; 30:0; 31:0; 32:0; 33:0; 34:0; 35:0; 36:0; 37:0; 38:+17; 39:20; 40:1608; 41:4011; 42:2978; 43:247; 44:082; 45:077; 46:+13.3; 47:999; 48:9999; 49:9999; 50:9999; 51:00000; 52:00000.000; 53:00000; 54:00000.000; 55:00000; 56:00000.000; 57:00000; 58:00000.000; 59:00000; 60:00000.000; 61:00000; 62:00000.000; 63:00000; 64:00000.000; 65:00000; 66:00000.000; 67:00000; 68:00000.000; 69:00000; 70:00000.000; 71:00000; 72:00000.000; 73:00000; 74:00000.000; 75:00000; 76:00000.000; 77:00000; 78:00000.000; 79:00000; 80:00000.000; 81:000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000; 521:99999; 522:99999; 523:9999; 524:999; 525:E8;'
@pytest.fixture()
def create_db_parsivel():
    """
    Creates test_parsivel.db in sample_data if it does not exist yet.
    """
    create_db_(db_path_parsivel)

@pytest.fixture()
def create_db_thies():
    """
    Creates test_thies.db in sample_data if it does not exist yet.
    """
    create_db_(db_path_thies)

def create_db_(db_path):
    """
    This function creates a database at the given path if it does not exist yet.
    :param db_path: the path to create a database at
    """
    if os.path.isfile(db_path):
        os.remove(db_path)
    create_db(dbpath=db_path)

@pytest.fixture()
def db_insert_24h_parsivel(create_db_parsivel): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts 24 hours worth of Parsivel telegrams into the test database.
    :param create_db_parsivel: the function to create the test database
    """
    db_insert_24h(db_path_parsivel, config_dict_parsivel, parsivel_lines)

@pytest.fixture()
def db_insert_24h_thies(create_db_thies): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts 24 hours worth of Thies telegrams into the test database.
    :param create_db_thies: the function to create the test database
    """
    db_insert_24h(db_path_thies, config_dict_thies, thies_lines)

def db_insert_24h(db_path, config_dict, telegram_lines):
    """
    This function inserts 24 hours worth of telegrams into a test database.
    :param db_path: the path to the database to insert data to
    :param config_dict: the combined site specific and general config files as a dictionary
    :param telegram_lines: the telegram lines to insert
    """
    # inserts 1440 rows to db
    con, cur = connect_db(dbpath=str(db_path))
    for i in range(data_points_24h):
        new_time = start_dt + timedelta(minutes=i)  # time offset: by 1 minute
        telegram = create_telegram(config_dict=config_dict,
                                    telegram_lines=telegram_lines,
                                    db_row_id=None,
                                    timestamp=new_time,
                                    db_cursor=cur,
                                    telegram_data={},
                                    logger=logger)
        telegram.insert2db()
    con.commit()
    cur.close()
    con.close()

@pytest.fixture()
def db_insert_24h_w_gaps_parsivel(create_db_parsivel): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts 24 hours worth of Parsivel telegrams into the test database, but with some missing rows.
    :param create_db_parsivel: the function to create the test database
    """
    db_insert_24h_w_gaps(db_path_parsivel, config_dict_parsivel, parsivel_lines)

@pytest.fixture()
def db_insert_24h_w_gaps_thies(create_db_thies): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts 24 hours worth of Thies telegrams into the test database, but with some missing rows.
    :param create_db_thies: the function to create the test database
    """
    db_insert_24h_w_gaps(db_path_thies, config_dict_thies, thies_lines)

def db_insert_24h_w_gaps(db_path, config_dict, telegram_lines):
    """
    This function inserts 24 hours worth of data into the test database, but with some missing rows.
    :param db_path: the path to the database to insert data to
    :param config_dict: the combined site specific and general config files as a dictionary
    :param telegram_lines: the telegram lines to insert
    """
    # inserts 1440 rows to db, but in half of entries, telegram is empty
    con, cur = connect_db(dbpath=str(db_path))
    for i in range(data_points_24h):
        new_time = start_dt + timedelta(minutes=i)  # time offset: by 1 minute
        if i % 2 == 0:
            data_lines = telegram_lines
        else:
            data_lines = []  # odd index: empty list, instead of parsivel_lines
        telegram = create_telegram(config_dict=config_dict,
                                    telegram_lines=data_lines,
                                    db_row_id=None,
                                    timestamp=new_time,
                                    db_cursor=cur,
                                    telegram_data={},
                                    logger=logger)
        telegram.insert2db()
    con.commit()
    cur.close()
    con.close()

@pytest.fixture()
def db_insert_24h_empty_parsivel(create_db_parsivel): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts 24 hours worth of empty Parsivel telegrams into the test database.
    :param create_db_parsivel: the function to create the test database
    """
    db_insert_24h_empty(db_path_parsivel, config_dict_parsivel)

@pytest.fixture()
def db_insert_24h_empty_thies(create_db_thies): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts 24 hours worth of empty Thies telegrams into the test database.
    :param create_db_thies: the function to create the test database
    """
    db_insert_24h_empty(db_path_thies, config_dict_thies)

def db_insert_24h_empty(db_path, config_dict):
    """
    This function inserts 24 hours worth of empty lines into a test database.
    :param db_path: the path to the database to insert data to
    :param config_dict: the combined site specific and general config files as a dictionary
    """
    # inserts 1440 rows to db, but in half of entries, telegram is empty
    con, cur = connect_db(dbpath=str(db_path))
    for i in range(data_points_24h):
        new_time = start_dt + timedelta(minutes=i)  # time offset: by 1 minute
        data_lines = []  # everything empty
        telegram = create_telegram(config_dict=config_dict,
                                    telegram_lines=data_lines,
                                    db_row_id=None,
                                    timestamp=new_time,
                                    db_cursor=cur,
                                    telegram_data={},
                                    logger=logger)
        telegram.insert2db()
    con.commit()
    cur.close()
    con.close()

def db_insert_two_telegrams(db_path, config_dict, telegram_lines):
    """
    This function inserts 1 telegram into a test database.
    :param db_path: the path to the database to insert data to
    :param config_dict: the combined site specific and general config files as a dictionary
    :param telegram_lines: the telegram lines to insert
    """
    con, cur = connect_db(dbpath=str(db_path))
    for i in range(2):
        new_time = start_dt + timedelta(minutes=i)  # time offset: by 1 minute
        telegram = create_telegram(config_dict=config_dict,
                                   telegram_lines=telegram_lines,
                                   db_row_id=None,
                                   timestamp=new_time,
                                   db_cursor=cur,
                                   telegram_data={},
                                   logger=logger)
        telegram.insert2db()
    con.commit()
    cur.close()
    con.close()

@pytest.fixture()
def db_insert_two_telegrams_thies(create_db_thies): # pylint: disable=unused-argument,redefined-outer-name
    """
    This function inserts two Thies telegrams into the test database.
    :param create_db_thies: the function to create the test database
    """
    db_insert_two_telegrams(db_path_thies, config_dict_thies, thies_lines)