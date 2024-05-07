import os
import subprocess
from datetime import datetime, timezone
from venv import logger
from netCDF4 import Dataset
from cftime import date2num
import numpy
import chardet
from sqlite3 import Cursor
from logging import Logger
from pathlib import Path
from typing import List, Dict, Union


class NowTime:
    '''
    Class dedicated to represent current date and time in different formats
    Attributes:
        utc : datetime object representing class instance time of instantiation
        time_list : list of hour,minutes,seconds of time of instantiation time
    '''

    def __init__(self):
        self.utc = datetime.now(timezone.utc)
        self.time_list = (self.utc.strftime("%H:%M:%S")).split(":")  # used to be: now_hour_min_secs
        # now_hour_min_secs = now_hour_min_secs.split(":")
        self.__date_strings()
        self.last_minute_of_day = self.utc.replace(hour=23, minute=59, second=0, microsecond=0)

    def __date_strings(self):
        '''
        def Converts instantiation time to different format class attributes
            iso: instantiation time in ISO 8601 format string
            ym: instantiation time YearMonth (YYYYmm) format string
            ymd: instantiation time YearMonthDay (YYYYmmdd) format string
        '''
        self.iso = self.utc.isoformat()
        self.ym = self.utc.strftime("%Y%m")
        self.ymd = self.utc.strftime("%Y%m%d")


class Telegram:
    '''
    Class dedicated to handling the returned the Parsivel telegram lines:
    * storing, processing and writing telegram to netCDF
    Note: f61 is handled a little differently as its values are multi-line, hence self.f61_rows
    '''

    def __init__(self, config_dict: Dict, telegram_lines: Union[str, bytes],
                 timestamp: datetime, db_cursor: Union[Cursor, None],
                 logger: Logger, telegram_data: Dict, db_row_id=None):
        '''
        initiates variables and methods:
        * set_netCDF_path
        * create_netCDF
        '''
        self.config_dict = config_dict
        self.telegram_lines = telegram_lines
        self.timestamp = timestamp  # <class 'datetime.datetime'> 2024-01-01 23:59:00+00:00
        self.delimiter = ';'
        self.logger = logger
        self.telegram_data = telegram_data
        self.db_cursor = db_cursor
        self.db_row_id = db_row_id

    def capture_prefixes_and_data(self):
        '''
        def Captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dict.
        '''
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

                super(Telegram, self).__setattr__(f'field_{field}_values', value)
                self.telegram_data[field] = value

    def parse_telegram_row(self):
        '''
        def parsers telegram string from SQL telegram field
        '''

        telegram_lines_list = self.telegram_lines.split('; ')

        try:
            telegram_lines_list[1]
        except IndexError:
            logger.error(msg=f"self.telegram_lines is EMPTY. self.telegram_lines: {self.telegram_lines}")
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

        self.__str2list(field='90', separator=',')
        self.__str2list(field='91', separator=',')
        self.__str2list(field='93', separator=',')

    def prep_telegram_data4db(self):
        '''
        transforms self.telegram_data items into self.telegram_data_str
        so that it can be easily inserted to SQL DB
        * key precedes value NN:val
        * key:value pair, seperated by '; '
        * list: converted to str with ',' separator between values
        * empty lists, empty strings: converted to 'None'
        Example: 19:None; 20:10; 21:25.05.2023;
        51:000140; 90:-9.999|-9.999|-9.999|-9.999|-9.999 ...
        '''
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
        self.logger.info(msg=f'inserting to DB: {self.timestamp.isoformat()}')
        insert = 'INSERT INTO disdrodl(timestamp, datetime, parsivel_id, telegram) VALUES'
        
        timestamp_str = self.timestamp.isoformat()
        ts = self.timestamp.timestamp()
        sensor = self.config_dict['global_attrs']['sensor_name']
        t_str = self.telegram_data_str
        
        insert_str = f"{insert} ({ts}, '{timestamp_str}', '{sensor}', '{t_str}');"

        self.logger.debug(msg=insert_str)
        self.db_cursor.execute(insert_str)

    def __str2list(self, field, separator):
        '''
        converts telegram_data values from string to list,
        by splitting at separator
        '''
        str_val = self.telegram_data[field]
        list_val = str_val.split(separator)
        self.telegram_data[field] = list_val


class NetCDF:
    def __init__(self, logger: Logger, config_dict: Dict, data_dir: Path, fn_start: str,
                 telegram_objs: List[Dict],
                 date: datetime) -> None:
        self.logger = logger
        self.config_dict = config_dict
        self.data_dir = data_dir
        self.fn_start = fn_start
        self.date_dt = date
        self.telegram_objs = telegram_objs
        logger.debug(msg="NetCDF class is initialized")


    def create_netCDF(self):
        '''
        def creates new netCDF file with global attributes, dimensions and variables (defined in yaml)
        '''
        self.__set_netCDF_path()
        netCDF_rootgrp = Dataset(self.path_netCDF, "w", format="NETCDF4")
        self.__global_attrs_to_netCDF(nc_rootgrp=netCDF_rootgrp)
        self.__netCDF_dimensions(nc_rootgrp=netCDF_rootgrp)
        self.__netcdf_variables(nc_rootgrp=netCDF_rootgrp)
        netCDF_rootgrp.close()
        self.logger.info(msg='class NetCDF executed create_netCDF()')

    def write_data_to_netCDF(self):
        '''
        def writes data to netCDF
        '''
        netCDF_rootgrp = Dataset(self.path_netCDF, "a", format="NETCDF4")

        # --- NetCDF variables NOT in telegram_data ---

        # var: time - appending timestamps to var time
        netCDF_var_time = netCDF_rootgrp.variables['time']
        value_list_dt = [telegram_obj.timestamp for telegram_obj in self.telegram_objs]
        time_value_list = [date2num(timestamp_val, units=netCDF_var_time.units, calendar=netCDF_var_time.calendar)
                           for timestamp_val in value_list_dt]
        netCDF_var_time[:] = time_value_list  # numpy.concatenate([netCDF_var_time[:].data, time_now_array])

        # NetCDF var: datetime (iso str values)
        netCDF_var_datetime = netCDF_rootgrp.variables['datetime']
        self.__netcdf_populate_s4_var(netCDF_var_=netCDF_var_datetime, var_key_='timestamp')

        # --- NetCDF variables in telegram_data ---
        for key in self.telegram_objs[0].telegram_data.keys():
            if key in self.config_dict['telegram_fields'].keys() and \
                    self.config_dict['telegram_fields'][key].get('include_in_nc') is True:
                field_dict = self.config_dict['telegram_fields'][key]
                standard_name = field_dict['var_attrs']['standard_name']
                netCDF_var = netCDF_rootgrp.variables[standard_name]

                # import pdb; pdb.set_trace()

                nc_details = f'Handling values from NetCDF var: {key}, {netCDF_var.standard_name}, {netCDF_var.dtype}, {netCDF_var._vltype}, {netCDF_var._isvlen}, dims: {netCDF_var._getdims()}'
                logger.debug(msg=nc_details)

                if netCDF_var.dtype == str:  # S4
                    # assuming S4 vars are only 1D - that's the case for parsivel
                    self.__netcdf_populate_s4_var(netCDF_var_=netCDF_var,
                                                  var_key_=key)
                else:
                    if len(netCDF_var._getdims()) <= 2:
                        all_items_val = [telegram_obj.telegram_data[key] for telegram_obj in self.telegram_objs]
                        netCDF_var[:] = all_items_val
                    elif len(netCDF_var._getdims()) > 2 and key == '93':
                        all_f93_items_val = []

                        for telegram_obj in self.telegram_objs:
                            try:
                                assert len(telegram_obj.telegram_data[key]) == 1024, 'telegram_obj.telegram_data["93"] len != 1024'
                            except AssertionError as error:
                                self.logger.error(msg=f'DB item {telegram_obj.db_row_id} from {telegram_obj.timestamp} {error}. 32x32 ndarray with (error value) -9.999 will be added instead')
                                error_f93 = numpy.full(shape=(32, 32), fill_value='-9999', dtype='<U3')
                                all_f93_items_val.append(error_f93)
                            else:
                                reshaped_f93 = numpy.array(telegram_obj.telegram_data[key]).reshape(32, 32)
                                all_f93_items_val.append(reshaped_f93)
                                self.logger.debug(msg=f'F93 values from DB item {telegram_obj.db_row_id} from {telegram_obj.timestamp} successfully reshaped')

                        netCDF_var[:] = all_f93_items_val

        netCDF_rootgrp.close()
        self.logger.info(msg='class NetCDF executed write_data_to_netCDF()')

    def compress(self):
        try:
            print(f'compress: {self.path_netCDF} ')
            subprocess.check_output(['nccopy', '-d9', self.path_netCDF, self.path_netCDF_temp])
        except subprocess.CalledProcessError as e:
            logger.error(msg=f'Failed to compress {self.path_netCDF}. Error code:{e.returncode} ')
            os.remove(self.path_netCDF_temp)
        else:
            logger.info(msg=f'Compressed netCDF {self.path_netCDF} successfully')
            print(f'compressed: {self.path_netCDF} ')

            # remove uncompressed and rename tmp to original filename
            os.remove(self.path_netCDF)
            os.rename(self.path_netCDF_temp, self.path_netCDF)

    def __set_netCDF_path(self):
        self.path_netCDF = self.data_dir / f'{self.fn_start}.nc'
        self.path_netCDF_temp = self.data_dir / f'tmp_{self.fn_start}.nc'

    def __netcdf_populate_s4_var(self, netCDF_var_, var_key_):
        '''
        - Populates NetCDF S4 vars -
        In Python netCDF4 lib the  dtype S4 (strings)
        are VLEN variables can only be assigned data
        one element at a time, with integer indices (not slices)
        '''
        if var_key_ in self.telegram_objs[0].telegram_data.keys():  # var in telegram
            for i, telegram_obj in enumerate(self.telegram_objs):
                netCDF_var_[i] = telegram_obj.telegram_data[var_key_]
        else:  # var NOT in telegram
            if netCDF_var_.standard_name == 'datetime':
                for i, telegram_obj in enumerate(self.telegram_objs):
                    netCDF_var_[i] = getattr(telegram_obj, 'timestamp').isoformat()
            else:
                for i, telegram_obj in enumerate(self.telegram_objs):
                    netCDF_var_[i] = getattr(telegram_obj, var_key_)

    def __netcdf_variables(self, nc_rootgrp):
        # nc_rootgrp, config_dict, timestamp, logger):
        '''
        Reads variables' definition from yaml config file and writes them to netCDF
        If variable values are set in the yml file def also assigns them their value
        '''
        # variables not in telegram
        for key, var_dict in self.config_dict['variables'].items():
            self.__set_netcdf_variable(key=key, one_var_dict=var_dict, nc_group=nc_rootgrp)
        for key, var_dict in self.config_dict['telegram_fields'].items():
            self.__set_netcdf_variable(key=key, one_var_dict=var_dict, nc_group=nc_rootgrp)

    def __set_netcdf_variable(self, key, one_var_dict, nc_group):
        self.logger.info(msg=f"creating netCDF variable {one_var_dict['var_attrs']['standard_name']}")
        if one_var_dict['include_in_nc'] is True:
            if one_var_dict['dtype'] != 'S4':  # can't compress variable-length str variables
                compression_method = 'zlib'
                # compression_method = dict(zlib=True, shuffle=True, complevel=5)
            else:
                compression_method = None

            if 'dimensions' not in one_var_dict.keys() or one_var_dict['dimensions'] is None:
                # scalar variables do not use dimensions
                variable = nc_group.createVariable(
                    one_var_dict['var_attrs']['standard_name'],
                    one_var_dict['dtype'],
                    fill_value=-1,
                    compression=compression_method,
                    complevel=9,
                    shuffle=True,
                    fletcher32=True)
            elif len(one_var_dict['dimensions']) >= 1:
                if 'fill_value' in one_var_dict.keys():
                    fill_val = one_var_dict['fill_value']
                else:
                    fill_val = -1

                variable = nc_group.createVariable(
                    one_var_dict['var_attrs']['standard_name'],
                    one_var_dict['dtype'],
                    tuple([dim for dim in one_var_dict['dimensions']]),
                    compression=compression_method,
                    fill_value=fill_val,
                )

            # fill (some) NetCDF variables' with predefine values
            if 'value' in one_var_dict.keys() and len(one_var_dict['value']) == 1:
                # use .assignValue() method for scalar values
                variable.assignValue(one_var_dict['value'])
            elif 'value' in one_var_dict.keys() and len(one_var_dict['value']) > 1:
                variable[:] = one_var_dict['value']

            # set NetCDF variables' attributes: units, comments, etc
            for var_attr in one_var_dict['var_attrs']:
                variable.__setattr__(var_attr, one_var_dict['var_attrs'][var_attr])
                
            if key == 'time':
                _start_dt = self.date_dt.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
                variable.__setattr__('units', f'hours since {_start_dt} +00:00')

    def __netCDF_dimensions(self, nc_rootgrp):
        '''
        reads dimensions from yaml config file and writes them to netCDF
        '''
        for key in self.config_dict['dimensions'].keys():
            self.logger.info(msg=f'creating netCDF dimension: {key}')
            nc_rootgrp.createDimension(key, self.config_dict['dimensions'][key]['size'])

    def __global_attrs_to_netCDF(self, nc_rootgrp):
        '''
        def writes global attributes (metadata) to newly created netCDF
        '''
        for key in self.config_dict['global_attrs'].keys():
            nc_rootgrp.__setattr__(key, self.config_dict['global_attrs'][key])


def unpack_telegram_from_db(telegram_str: str) -> Dict[str, Union[str, list]]:
    '''
    unpacks telegram string from sqlite DB row into a dictionary

    * key precedes value NN:val
    * key:value pair, seperated by '; '
    * list: converted to str with ',' separator between values
    * empty lists, empty strings: converted to 'None'
    Example Input: '19:None; 20:10; 21:25.05.2023;
    51:000140; 90:-9.999,-9.999,-9.999,-9.999,-9.999 ...'
    Example Output:  {'60': '00000062', '90': '-9.999,-9.999,01.619,...'}
    '''
    telegram_dict = {}
    telegram_list = telegram_str.split('; ')

    for telegram_item in telegram_list:
        key, val = telegram_item.split(':')
        if val == 'None':
            val = None
        telegram_dict[key] = val

    return telegram_dict
