"""
This module contains tests for the NowTime and methods in the telegram file.

Functions:
- test_NowTime: Tests that the NowTime class functions in general, and returns the correct time.
- test_timestamp: Tests the correctness of the iso format strings from the NowTime class.
- create_test_data_dir: Creates a directory at the given path if it doesn't exist yet.
- test_parse_telegram_row_edge_cases: Tests that a telegram row with key:val,val,...; for some pair can be parsed.
- test_create_telegram_not_recognized: Tests parsing a non recognized sensor type.
"""

import os
import logging
from logging import StreamHandler
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
from pydantic.v1.utils import deep_update

from modules import telegram
from modules.now_time import NowTime
from modules.telegram import ParsivelTelegram
from modules.util_functions import yaml2dict


log_handler = StreamHandler()
logger = logging.getLogger('testlog')
logger.addHandler(log_handler)
wd = Path(__file__).parent.parent
test_data_dir = wd / 'test_data'
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_PAR_008_GV.yml')
config_dict = deep_update(config_dict, config_dict_site)

config_dict_thies = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_thies.yml')
config_dict_site_thies = yaml2dict(path=wd / 'configs_netcdf' / 'config_THIES_006_GV.yml')
config_dict_thies = deep_update(config_dict_thies, config_dict_site_thies)

parsivel_lines = [b'TYP OP4A\r\n', b'01:0000.000\r\n', b'02:0000.00\r\n', b'03:00\r\n', b'04:00\r\n', b'05:   NP\r\n', b'06:   C\r\n', b'07:-9.999\r\n', b'08:20000\r\n', b'09:00043\r\n', b'10:13894\r\n', b'11:00000\r\n', b'12:021\r\n', b'13:450994\r\n', b'14:2.11.6\r\n', b'15:2.11.1\r\n', b'16:0.50\r\n', b'17:24.3\r\n', b'18:0\r\n', b'19: \r\n', b'20:10:13:21\r\n', b'21:25.05.2023\r\n', b'22:\r\n', b'23:\r\n', b'24:0000.00\r\n', b'25:000\r\n', b'26:032\r\n', b'27:022\r\n', b'28:022\r\n', b'29:000.041\r\n', b'30:00.000\r\n', b'31:0000.0\r\n', b'32:0000.00\r\n', b'34:0000.00\r\n', b'35:0000.00\r\n', b'40:20000\r\n', b'41:20000\r\n', b'50:00000000\r\n', b'51:000140\r\n', b'90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\r\n', b'91:00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;\r\n', b'93:000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;\r\n', b'94:0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;\r\n', b'95:0.00;0.00;0.00;0.00;0.00;0.00;0.00;\r\n', b'96:0000000;0000000;0000000;0000000;0000000;0000000;0000000;\r\n', b'97:;\r\n', b'98:;\r\n', b'99:;\r\n', b'\x03'] # pylint: disable=line-too-long
parsivel_db_line_edge_case = '01:0000.000; 02:0000.00; 03:1;2; 90:0,0; 91:0,0; 93:0,0'

def test_NowTime():
    """
    This function tests that the NowTime class functions in general, and returns the correct time.
    """
    now = NowTime()
    test_time_list = datetime.utcnow().strftime("%H:%M:%S").split(":")
    assert isinstance(now.time_list, list) is True
    assert now.time_list[0] == test_time_list[0]
    assert now.time_list[1] == test_time_list[1]
    assert now.time_list[2] == test_time_list[2]
    # assert: the following attributes are only created after method: __date_strings()
    assert isinstance(now.iso, str) is True
    assert isinstance(now.ym, str) is True
    assert isinstance(now.ymd, str) is True


def test_timestamp():
    """
    This functions tests the correctness of the iso format strings from the NowTime class.
    """
    now = NowTime()
    print('now.utc', now.utc)
    print('now.utc (iso)', now.utc.isoformat())
    ts = now.utc.timestamp()
    ts_no_tz = datetime.fromtimestamp(ts)
    ts_tz = datetime.fromtimestamp(ts, tz=timezone.utc)
    assert ts_tz.isoformat() == now.utc.isoformat()
    assert ts_no_tz.isoformat() != now.utc.isoformat()  # no tz aware date will differ from tzaware
    # print('now.utc.timestamp', ts)
    # print('ts_no_tz', ts_no_tz)
    # print('utcfromtimestamp', datetime.utcfromtimestamp(ts))
    # print('ts_tz', ts_tz)

def create_test_data_dir(directory):
    """
    This functions creates a directory at the given path if it doesn't exist yet.
    """
    if not os.path.exists(path=directory):
        os.mkdir(path=directory)


def test_create_telegram_not_recognized(caplog):
    """
    Tests that if a configuration dictionary for a not recognized disdrometer sensor is
    parsed the logger sends a message and the function returns None.
    """
    config_dict = MagicMock()
    values = { 'global_attrs': {'sensor_type':'wrong_telegram'} }
    config_dict.__getitem__.side_effect = values.__getitem__
    assert config_dict['global_attrs']['sensor_type'] == 'wrong_telegram'
    created_telegram = telegram.create_telegram(config_dict=config_dict,
                                                telegram_lines=None,
                                                db_row_id=None,
                                                timestamp=None,
                                                db_cursor=None,
                                                telegram_data={},
                                                logger=logger)
    assert [r.msg for r in caplog.records][0] == 'Sensor type wrong_telegram not recognized'
    assert created_telegram is None

