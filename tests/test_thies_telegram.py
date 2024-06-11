"""
Module that tests Thies telegram methods.

Functions:
- test_capture_prefixes_and_data: Tests the correctness of capturing telegram data.
- test_capture_prefixes_and_data_empty: Tests the correctness of capturing telegram when telegram is empty.
- test_capture_prefixes_and_data_partial_telegram: Tests the correctness of capturing telegram data when
  only a partial Thies telegram is given.
- test_capture_prefixes_and_data_one_missing_value: Tests the correctness of capturing telegram data when
  a Thies telegram with a missing value is given.
- test_parse_thies_telegram_row: Tests the correctness of creating a ThiesTelegram object with contents.
- test_parse_thies_empty_telegram_row: Tests the correctness of creating a ThiesTelegram object without contents.
- test_parse_telegram_row_missing_value: Tests the correctness of creating a ThiesTelegram object with one value
  missing.
- test_parse_telegram_row_edge_cases: Tests 2 edge cases. Parsing a telegram row with a key that has assigned
  multiple values (key:val;val;) and parsing a telegram with a key that is not in the configuration
  dictionary of the sensor.
"""

import logging
import os
from pathlib import Path
from logging import StreamHandler
from datetime import datetime, timezone

from pydantic.v1.utils import deep_update

from modules.sqldb import connect_db, query_db_rows_gen
from modules.util_functions import yaml2dict
from modules.now_time import NowTime
from modules.telegram import ThiesTelegram

now = NowTime()
wd = Path().resolve()
data_dir = wd / 'sample_data'
db_file_thies = 'test_thies.db'
db_path_thies = data_dir / db_file_thies

log_handler = StreamHandler()
logger = logging.getLogger('test-log')
logger.addHandler(log_handler)

config_dict_thies = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_thies.yml')
config_dict_site_thies = yaml2dict(path=wd / 'configs_netcdf' / 'config_006_GV_THIES.yml')
config_dict_thies = deep_update(config_dict_thies, config_dict_site_thies)

start_dt_thies = datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)

thies_lines = '06;0854;2.11;01.01.14;18:59:00;00;00;NP   ;000.000;00;00;NP   ;000.000;000.000;000.000;0000.00;99999;-9.9;100;0.0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;+23;26;1662;4011;2886;258;062;063;+20.3;999;9999;9999;9999;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;99999;99999;9999;999;E9;' # pylint: disable=line-too-long
keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '521', '522', '523', '524', '525']
matrix_values = '000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000'
thies_lines_empty = ''
thies_lines_partial = '06;0854;2.11;01.01.14;18:59:00;00;00;NP   ;000.000;00;00;NP   ;'

thies_db_line = '1:06; 2:06; 3:0854; 4:2.11; 5:01.01.14; 6:18:59:00; 7:00; 8:00; 9:NP   ; 10:000.000; 11:00; 12:00; 13:NP   ; 14:000.000; 15:000.000; 16:000.000; 17:0000.00; 18:99999; 19:-9.9; 20:100; 21:0.0; 22:0; 23:0; 24:0; 25:0; 26:0; 27:0; 28:0; 29:0; 30:0; 31:0; 32:0; 33:0; 34:0; 35:0; 36:0; 37:0; 38:+23; 39:26; 40:1662; 41:4011; 42:2886; 43:258; 44:062; 45:063; 46:+20.3; 47:999; 48:9999; 49:9999; 50:9999; 51:00000; 52:00000.000; 53:00000; 54:00000.000; 55:00000; 56:00000.000; 57:00000; 58:00000.000; 59:00000; 60:00000.000; 61:00000; 62:00000.000; 63:00000; 64:00000.000; 65:00000; 66:00000.000; 67:00000; 68:00000.000; 69:00000; 70:00000.000; 71:00000; 72:00000.000; 73:00000; 74:00000.000; 75:00000; 76:00000.000; 77:00000; 78:00000.000; 79:00000; 80:00000.000; 81:000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000,000; 521:99999; 522:99999; 523:9999; 524:999; 525:E9'
thies_lines_missing_value = '06;;2.11;01.01.14;18:59:00;00;00;NP   ;000.000;00;00;NP   ;000.000;000.000;000.000;0000.00;99999;-9.9;100;0.0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;+23;26;1662;4011;2886;258;062;063;+20.3;999;9999;9999;9999;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;99999;99999;9999;999;E9;' # pylint: disable=line-too-long
thies_db_line_partial = '1:06; 2:06; 3:0854; 4:2.11; 5:01.01.14; 6:18:59:00; 7:00; 8:00; 9:NP   ;'
thies_db_line_edge_case ='1:06; 2:1;2; 3:0854; 4:2.11; 5:01.01.14; 6:18:59:00; 7:00; 8:00; 9:NP   ; 81:0,0; 800:'
log_handler = StreamHandler()
logger = logging.getLogger('test-log')
logger.addHandler(log_handler)

def test_capture_prefixes_and_data():
    """
    This function tests that the capture_prefixes_and_data method correctly fills
    the telegram data dictionary.
    """
    telegram = ThiesTelegram(config_dict=None,
                             telegram_lines=thies_lines,
                             timestamp=None,
                             db_cursor=None,
                             telegram_data={},
                             logger=None)
    telegram.capture_prefixes_and_data()

    data_dictionary = telegram.telegram_data
    #check that all the keys are in the dictionary
    assert list(data_dictionary.keys()) == keys
    #check that values from telegram are populated to dictionary
    assert data_dictionary['5'] == '01.01.14'
    assert data_dictionary['6'] == '18:59:00'
    #check that values for 22x20 matrix are correctly added
    assert data_dictionary['81'] == matrix_values

def test_capture_prefixes_and_data_empty():
    """
    This function tests that the capture_prefixes_and_data method correctly fills
    the telegram data dictionary when an empty telegram is given.
    """
    telegram = ThiesTelegram(config_dict=None,
                             telegram_lines=thies_lines_empty,
                             timestamp=None,
                             db_cursor=None,
                             telegram_data={},
                             logger=None)
    telegram.capture_prefixes_and_data()

    data_dictionary = telegram.telegram_data
    #check that telegram data is empty
    assert len(data_dictionary.keys()) == 0

def test_capture_prefixes_and_data_partial_telegram():
    """
    This function tests that the capture_prefixes_and_data method correctly fills
    the telegram data dictionary when a partial telegram is given.
    """
    telegram = ThiesTelegram(config_dict=None,
                             telegram_lines=thies_lines_partial,
                             timestamp=None,
                             db_cursor=None,
                             telegram_data={},
                             logger=None)
    telegram.capture_prefixes_and_data()

    data_dictionary = telegram.telegram_data
    #check that telegram data dictionary is empty, partial telegrams are not parsed
    assert len(data_dictionary.keys()) == 0

def test_capture_prefixes_and_data_one_missing_value():
    """
    This function tests that the capture_prefixes_and_data method correctly fills
    the telegram data dictionary when a telegram with one missing value (val;;val;) is given.
    """
    telegram = ThiesTelegram(
        config_dict=config_dict_thies,
        telegram_lines=thies_lines,
        timestamp=now.utc,
        db_cursor=None,
        telegram_data={},
        logger=None)
    telegram.capture_prefixes_and_data()
    assert telegram.telegram_data['3'] == '0854'
    telegram.telegram_data['3'] = ''
    telegram.prep_telegram_data4db()
    telegram_str_list = telegram.telegram_data_str.split('; ')
    assert telegram_str_list[2] == '3:None'


def test_parse_thies_telegram_row(db_insert_two_telegrams_thies):
    """
    This function tests the correctness of creating a ThiesTelegram object with contents.
    :param db_insert_two_telegrams_thies: the function inserts 2 telegrams into the database.
    """
    con, cur = connect_db(dbpath=str(db_path_thies))
    row = next(query_db_rows_gen(con=con, date_dt=start_dt_thies, logger=logger))
    ts_dt = datetime.fromtimestamp(row.get('timestamp'), tz=timezone.utc)
    row_telegram = ThiesTelegram(
        config_dict=config_dict_thies,
        telegram_lines=row.get('telegram'),
        timestamp=ts_dt,
        db_cursor=None,
        telegram_data={},
        logger=None)
    row_telegram.parse_telegram_row()

    data_dictionary = row_telegram.telegram_data
    # check that all the keys are in the dictionary
    assert list(data_dictionary.keys()) == keys
    # check that values from telegram are populated to dictionary
    assert data_dictionary['5'] == '01.01.14'
    assert data_dictionary['6'] == '18:59:00'
    # check that values for 22x20 matrix are correctly added
    assert data_dictionary['81'] == matrix_values.split(',')
    assert len(data_dictionary['81']) == 440
    for i in row_telegram.telegram_data['81']:
        assert (len(i) == 3 or len(i) == 4)  and ',' not in i
    # check that each key is also in configuration dictionary
    for key in row_telegram.telegram_data.keys():
        assert key in config_dict_thies['telegram_fields']
    cur.close()
    con.close()


def test_parse_thies_empty_telegram_row(db_insert_two_telegrams_thies):
    """
    This function tests the correctness of creating a ThiesTelegram object without contents.
    """
    con, cur = connect_db(dbpath=str(db_path_thies))
    row = next(query_db_rows_gen(con=con, date_dt=start_dt_thies, logger=logger))
    ts_dt = datetime.fromtimestamp(row.get('timestamp'), tz=timezone.utc)
    row_telegram = ThiesTelegram(
        config_dict=config_dict_thies,
        telegram_lines='',
        timestamp=ts_dt,
        db_cursor=None,
        telegram_data={},
        logger=None)
    row_telegram.parse_telegram_row()
    # check that telegram data dictionary is empty
    assert row_telegram.telegram_data == {}
    cur.close()
    con.close()
    os.remove(db_path_thies)

def test_parse_telegram_row_missing_value():
    """
    This function tests the correctness of creating a ThiesTelegram object with contents, but
    with one value missing.
    """
    telegram = ThiesTelegram(
        config_dict=config_dict_thies,
        telegram_lines=thies_lines_missing_value,
        timestamp=now.utc,
        db_cursor=None,
        telegram_data={},
        logger=None)
    telegram.capture_prefixes_and_data()
    telegram.parse_telegram_row()
    #test that telegragram with missing value has key associated to it
    #but the value is ''-> fill value
    assert len(telegram.telegram_data) == 86
    assert '3' in telegram.telegram_data.keys()
    assert telegram.telegram_data['3'] == ''

def test_parse_telegram_row_edge_cases():
    """
    This function tests 2 edge cases. Parsing a telegram row with a key that has assigned
    multiple values (key:val;val;) and parsing a telegram with a key that is not in the configuration
    dictionary of the sensor.
    """
    telegram = ThiesTelegram(
        config_dict=config_dict_thies,
        telegram_lines=thies_db_line_edge_case,
        timestamp=now.utc,
        db_cursor=None,
        telegram_data={},
        logger=None)
    telegram.parse_telegram_row()
    assert telegram.telegram_data['2'] == ['1','2']
    assert '800' not in telegram.telegram_data.keys()
