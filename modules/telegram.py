"""
This module contains the partly abstract class for handling telegrams received from the sensors and database,
and the implementation of different telegram classes inheriting this class.

Functions:
- create_telegram: Creates a specific Telegram object based on the sensor type in the configuration dictionary.
"""

from abc import abstractmethod, ABC
from datetime import datetime
from venv import logger as telegram_logger
from sqlite3 import Cursor
from logging import Logger
from typing import Dict, Union
import chardet


class Telegram(ABC):
    """
    Abstract class dedicated to handling the returned telegram lines:
    * storing, processing and writing telegram to netCDF
    Note: f61 is handled a little differently as its values are multi-line, hence self.f61_rows

    Attributes:
    - config_dict: dictionary for later exporting into netcdf
    - telegram_lines: lines of the telegram received from a sensor
    - timestamp: the time
    - delimiter: the delimiter used in the telegram
    - db_cursor: database cursor
    - logger: logger logging data from a sensor
    - telegram_data: data from the telegram sent by a sensor
    - db_row_id: row id from the database
    - telegram_data_str: telegram data string

    Functions:
    - capture_prefixes_and_data: captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dict
    - parse_telegram_row: parses telegram string from SQL telegram field
    - prep_telegram_data4db: transforms self.telegram_data so that it can be easily inserted to SQL DB
    - insert2db: inserts telegram strings into the database
    - Functions:
    - str2list: Converts telegram_data values from string to list by splitting at the specified separator.
    """

    def __init__(self, config_dict: Dict, telegram_lines: Union[str, bytes],
                 timestamp: datetime, db_cursor: Union[Cursor, None],
                 logger: Logger, telegram_data: Dict, db_row_id=None, telegram_data_str=None):
        """
        Constructor for telegram class
        :param config_dict: dictionary for later exporting into netcdf
        :param telegram_lines: lines of the telegram received from a sensor
        :param timestamp: the time
        :param db_cursor: database cursor
        :param logger: logger logging data from a sensor
        :param telegram_data: data from the telegram sent by a sensor
        :param db_row_id: row id from the database
        :param telegram_data_str: telegram data string
        """
        self.config_dict = config_dict
        self.telegram_lines = telegram_lines
        self.timestamp = timestamp  # <class 'datetime.datetime'> 2024-01-01 23:59:00+00:00
        self.delimiter = ';'
        self.logger = logger
        self.telegram_data = telegram_data
        self.db_cursor = db_cursor
        self.db_row_id = db_row_id
        self.telegram_data_str = telegram_data_str

    @abstractmethod
    def capture_prefixes_and_data(self):
        """
        Abstract method that captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dict.
        """

    @abstractmethod
    def parse_telegram_row(self):
        """
        Abstract method that parses telegram string from SQL telegram field.
        """

    def prep_telegram_data4db(self):
        """
        Transforms self.telegram_data items into self.telegram_data_str
        so that it can be easily inserted to SQL DB.
        * key precedes value NN:val
        * key:value pair, seperated by '; '
        * list: converted to str with ',' separator between values
        * empty lists, empty strings: converted to 'None'
        Example: 19:None; 20:10; 21:25.05.2023;
        51:000140; 90:-9.999|-9.999|-9.999|-9.999|-9.999 ...
        """
        self.telegram_data_str = ''

        for key, val in self.telegram_data.items():
            dt_str = f'{key}:'

            if isinstance(val, list):
                if len(val) == 0:
                    dt_str += 'None'
                else:
                    dt_str += (',').join(val)
            elif isinstance(val, str):
                if len(val) == 0:
                    dt_str += 'None'
                else:
                    dt_str += val

            self.telegram_data_str += dt_str
            self.telegram_data_str += '; '

        self.telegram_data_str = self.telegram_data_str[:-2]  # remove last '; '


    def insert2db(self):
        """"
        Method for passing telegrams strings into the database
        """
        self.capture_prefixes_and_data()
        self.prep_telegram_data4db()

        self.logger.info(msg=f'inserting to DB: {self.timestamp.isoformat()}')
        insert = 'INSERT INTO disdrodl(timestamp, datetime, parsivel_id, telegram) VALUES'

        timestamp_str = self.timestamp.isoformat()
        ts = self.timestamp.timestamp()
        sensor = self.config_dict['global_attrs']['sensor_name']
        t_str = self.telegram_data_str

        insert_str = f"{insert} ({ts}, '{timestamp_str}', '{sensor}', '{t_str}');"

        self.logger.debug(msg=insert_str)
        self.db_cursor.execute(insert_str)


    def str2list(self, field, separator):
        """
        Converts telegram_data values from string to list by splitting at the specified separator.

        :param field: indicates the data to be split into a list
        :param separator: the separator to split at
        """
        str_val = self.telegram_data[field]
        list_val = str_val.split(separator)
        self.telegram_data[field] = list_val


class ParsivelTelegram(Telegram):
    """
    Class dedicated to handling the returned the Parsivel telegram lines:
    * storing, processing and writing telegram to netCDF.
    Note: f61 is handled a little differently as its values are multi-line, hence self.f61_rows.
    """

    def capture_prefixes_and_data(self):
        """
        Captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dict.
        """
        for line in self.telegram_lines:
            encoding = chardet.detect(line)['encoding']
            line_str = line.decode(encoding)
            line_list = line_str.split(":")

            if len(line_list) > 1 and line_list[1].strip() != self.delimiter:
                field = line_list[0]
                value = line_list[1].strip()  # strip white space
                value_list = value.split(self.delimiter)
                value_list = [v for v in value_list if len(v) > 0]

                if len(value_list) == 1:
                    value = value_list[0]
                else:
                    value = value_list

                super().__setattr__(f'field_{field}_values', value)
                self.telegram_data[field] = value


    def parse_telegram_row(self):
        """
        Parses telegram string from SQL telegram fields.
        """
        telegram_lines_list = self.telegram_lines.split('; ')

        try:
            telegram_lines_list[1]
        except IndexError:
            telegram_logger.error(msg=f"self.telegram_lines is EMPTY. self.telegram_lines: {self.telegram_lines}")
            return

        for keyval in telegram_lines_list:
            keyval_list = keyval.split(':')

            if keyval_list[0] in self.config_dict['telegram_fields'].keys() and \
                    len(keyval_list) > 1 and keyval_list[1].strip() != self.delimiter:
                field = keyval_list[0]
                value = keyval_list[1].strip()  # strip white space
                value_list = value.split(self.delimiter)
                value_list = [v for v in value_list if len(v) > 0]

                if len(value_list) == 1:
                    value = value_list[0]
                else:
                    value = value_list

                self.telegram_data[field] = value

        self.str2list(field='90', separator=',')
        self.str2list(field='91', separator=',')
        self.str2list(field='93', separator=',')


class ThiesTelegram(Telegram):
    """
    Class dedicated to handling the returned the Thies telegram lines:
    * storing, processing and writing telegram to netCDF.
    """

    def capture_prefixes_and_data(self):
        """
        Captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dictionary.
        """
        # check if given telegram is an empty string
        if len(self.telegram_lines) == 0:
            return
        # split telegram string into individual values
        telegram_list_stx_and_id_combined = self.telegram_lines.split(';')

        # separate start of text character from device id
        telegram_stx_and_id = telegram_list_stx_and_id_combined[0].split()
        telegram_stx = telegram_stx_and_id[0]
        telegram_device_id = telegram_stx_and_id[-2:]
        telegram_list = telegram_list_stx_and_id_combined[1:]
        telegram_list.insert(0, telegram_stx)
        telegram_list.insert(0, telegram_device_id)

        # check if telegram is has correct number of values
        if(len(telegram_list) != 526):
           telegram_logger.error(msg=f"telegram is missing values")
           return

        # put telegram values into telegram dictionary
        for index,value in enumerate(telegram_list[:-1]):
            if index == 80:
                self.telegram_data['81'] = value
                super().__setattr__(f'field_{index+1}_values', value)
            if 81 <= index <= 519:
                self.telegram_data['81'] = self.telegram_data['81'] + ',' + value
                super().__setattr__(f'field_{81}_values', value)
            else:
                self.telegram_data[str(index+1)] = value
                super().__setattr__(f'field_{index+1}_values', value)


    def parse_telegram_row(self):
        """
        Parses telegram string from SQL database telegram fields.
        """

        telegram_lines_list = self.telegram_lines.split('; ')
        try:
            telegram_lines_list[1]
        except IndexError:
            telegram_logger.error(msg=f"self.telegram_lines is EMPTY. self.telegram_lines: {self.telegram_lines}")
            return

        for keyval in telegram_lines_list:
            # check if telegram value is sensor time (has format 6:XX:XX:XX)
            if len(keyval) > 0 and keyval[0] == '6':
                keyval_list = keyval.split(':',1)
            else:
                keyval_list = keyval.split(':')

            if keyval_list[0] not in self.config_dict['telegram_fields'].keys() or\
                    len(keyval_list) <= 1 or keyval_list[1].strip() == self.delimiter:
                continue

            field = keyval_list[0]
            value = keyval_list[1].strip()  # strip white space
            value_list = value.split(self.delimiter)
            value_list = [v for v in value_list if len(v) > 0]

            if len(value_list) == 1:
                value = value_list[0]
            else:
                value = value_list

            self.telegram_data[field] = value

        # add 440 value array representing 22x20 matrix
        self.str2list(field='81', separator=',')


def create_telegram(config_dict: Dict, telegram_lines: Union[str, bytes],
                 timestamp: datetime, db_cursor: Union[Cursor, None],
                 logger: Logger, db_row_id: Union[Cursor, None], telegram_data: Dict) -> Union[Telegram, None]: # pylint: disable=unused-argument
    """
    Creates a specific Telegram object based on the sensor type in the configuration dictionary.
    :param config_dict: dictionary for later exporting into netcdf
    :param telegram_lines: lines of the telegram received from a sensor
    :param timestamp: the time
    :param db_cursor: database cursor
    :param logger: logger logging data from a sensor
    :param telegram_data: data from the telegram sent by a sensor
    :param db_row_id: row id from the database
    :return: the respective Telegram object for a recognized sensor type, or None otherwise
    """
    sensor_type = config_dict['global_attrs']['sensor_type']

    # Create dictionary with the sensor types as keys and the respective Telegram classes as values
    sensors = {"OTT Hydromet Parsivel2": ParsivelTelegram, "Thies Clima": ThiesTelegram}

    try:
        telegram_obj = sensors[sensor_type](config_dict=config_dict,
                                            telegram_lines=telegram_lines,
                                            db_row_id=db_row_id,
                                            timestamp=timestamp,
                                            db_cursor=db_cursor,
                                            telegram_data=telegram_data,
                                            logger=logger)
        return telegram_obj
    except KeyError:
        # If the sensor type is not recognized, log an error and return None
        logger.error(msg=f"Sensor type {sensor_type} not recognized")
        return None

    