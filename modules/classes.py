import os
import subprocess
from datetime  import datetime, timedelta
from netCDF4 import Dataset
from cftime import date2num
import numpy
import chardet
from typing import Dict, Union


class NowTime:
    '''
    Class dedicated to represent current date and time in different formats
    Attributes:
        utc : datetime object representing class instance time of instantiation
        time_list : list of hour,minutes,seconds of time of instantiation time
    '''
    def __init__(self):
        self.utc = datetime.utcnow()
        self.time_list = (self.utc.strftime("%H:%M:%S")).split(":")  # used to be: now_hour_min_secs
        # now_hour_min_secs = now_hour_min_secs.split(":")
        self.date_strings()
        self.last_minute_of_day = self.utc.replace(hour=23, minute=59, second=0, microsecond=0)

    def date_strings(self):
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
    def __init__(self, config_dict, telegram_lines, timestamp, db_cursor, logger, telegram_data={}):
        '''
        initiates variables and methods:
        * set_netCDF_path
        * create_netCDF
        '''
        self.config_dict = config_dict
        self.telegram_lines = telegram_lines
        self.timestamp = timestamp
        self.delimiter = ';'
        self.logger = logger
        self.telegram_data = telegram_data
        self.db_cursor = db_cursor
        # print(telegram_data)

    def capture_prefixes_and_data(self):
        '''
        def Captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dict.
        '''
        for i in self.telegram_lines:
            encoding = chardet.detect(i)['encoding']
            i_str = i.decode(encoding)
            i_list = i_str.split(":")
            if len(i_list) > 1 and i_list[1].strip() != self.delimiter:
                field = i_list[0]
                value = i_list[1].strip()  # strip white space
                value_list = value.split(self.delimiter)
                value_list = [v for v in value_list if len(v) > 0]
                if len(value_list) == 1:
                    value = value_list[0]
                else:
                    value = value_list
                super(Telegram, self).__setattr__(f'field_{field}_values', value)
                self.telegram_data[field] = value

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
        self.telegram_data_str = self.telegram_data_str[:-2] # remove last '; '

    def insert2db(self):
        self.prep_telegram_data4db()
        print('inserting to DB', self.timestamp.isoformat())
        timestamp_str = self.timestamp.isoformat()  
        insert_str = f"INSERT INTO disdrodl(timestamp, datetime, parsivel_id, telegram) VALUES ({self.timestamp.timestamp()}, '{timestamp_str}',  '{self.config_dict['global_attrs']['sensor_name']}', '{self.telegram_data_str}');"
        print(insert_str)
        self.db_cursor.execute(insert_str)

    def query_db(self, start_dt, end_dt):
        q_select = 'SELECT id, timestamp, datetime, parsivel_id, telegram'
        q_from = 'FROM disdrodl'
        q_where = f'WHERE timestamp >= {start_dt.timestamp()} AND timestamp < {end_dt.timestamp()}'
        select = f'{q_select} {q_from} {q_where}'
        res = self.db_cursor.execute(select)
        for row in res.fetchall():
            id, timestamp, dt, parsivel_id, telegram_ = row
            row_dict = unpack_telegram_from_db(telegram_str=telegram_)
            # TODO: continue when writing the 24h-rows to netCDF 
            # for the moment will append to tmp var self.db

            print(id, dt)
            # assert there is no ; in values
            # import pdb; pdb.set_trace()
        # TODO: move query DB to another class
    

    def str2list(self, field, separator):
        '''
        converts telegram_data values from string to list, 
        by splitting at separator
        '''
        str_val = self.telegram_data[field]
        list_val = str_val.split(separator)
        self.telegram_data[field] = list_val

    def set_netCDF_path(self):
        self.path_netCDF = self.data_dir / f'{self.data_fn_start}.nc'
        self.path_netCDF_temp = self.data_dir / f'tmp_{self.data_fn_start}.nc'
        # TODO: move var assignment to __init__
        #TODO: set path self.path_netCDF_f61

    def create_netCDF(self):
        '''
        def creates new netCDF file with global attributes, dimensions and variables (defined in yaml) 
        TODO: create new netCDF for F61 at self.path_netCDF_f61

        '''
        if not os.path.exists(self.path_netCDF):
            netCDF_rootgrp = Dataset(self.path_netCDF, "w", format="NETCDF4")
            # netCDF_rootgrp.set_fill_on()
            global_attrs_to_netCDF(nc_rootgrp=netCDF_rootgrp, config_dict=self.config_dict)
            netCDF_dimensions(nc_rootgrp=netCDF_rootgrp, config_dict=self.config_dict, logger=self.logger)
            netCDF_variables(nc_rootgrp=netCDF_rootgrp, config_dict=self.config_dict, timestamp=self.timestamp,logger=self.logger)
            netCDF_rootgrp.close()
    
    def append_data_to_netCDF(self):
        '''
        def appends data to netCDF (path_netCDF)
        TODO: append data to self.path_netCDF_f61
        '''
        netCDF_rootgrp = Dataset(self.path_netCDF, "a", format="NETCDF4")        
        # (time) appending timestamps to var time
        netCDF_var_time = netCDF_rootgrp.variables['time']
        time_now_array = date2num([self.timestamp], units=netCDF_var_time.units,calendar=netCDF_var_time.calendar)
        netCDF_var_time[:] = numpy.concatenate([netCDF_var_time[:].data, time_now_array])
        # currentindex: write data to *this* slot(currentindex)
        currentindex = len(netCDF_var_time[:].data) - 1  
        timestamp_var = netCDF_rootgrp.variables['timestamp']
        timestamp_var[currentindex] = self.timestamp.strftime('%Y-%m-%dT%H:%M:%S') # timestamp str
        # print(self.telegram_data)
        for key, value in self.telegram_data.items():
            if key in self.config_dict['telegram_fields'].keys() and \
                    self.config_dict['telegram_fields'][key].get('include_in_nc') is True:
                field_dict = self.config_dict['telegram_fields'][key]
                standard_name = field_dict['var_attrs']['standard_name']
                netCDF_var = netCDF_rootgrp.variables[standard_name]
                # print(key,  '-- IN config_dict[telegram_fields] --',netCDF_var.standard_name )
                # print(key, netCDF_var.standard_name, standard_name, value)
                # print(type(value))

                if isinstance(value, str):
                    netCDF_var[currentindex] = value
                elif isinstance(value, list):
                    # print(f'list value: {value}')
                    # print(f'telegram key:{key}; index:{currentindex}; str value: {value}')
                    value_np_array = numpy.array(value)
                    if key == '93':
                        value_np_array = value_np_array.reshape(32,32)
                    elif key == '61':
                        pass
                        # print('TODO: F61') 
                        # TODO: F61 write to another file
                    netCDF_var[currentindex] = value_np_array
                    pass # handle list fields one by one
        netCDF_rootgrp.close()
    
    def compress_netcdf(self):        
        subprocess.run(['nccopy', '-d6', self.path_netCDF, self.path_netCDF_temp])
        self.logger.info(msg=f'Compressed netCDF {self.path_netCDF}')
        os.remove(self.path_netCDF)
        os.rename(self.path_netCDF_temp, self.path_netCDF)

def global_attrs_to_netCDF(nc_rootgrp, config_dict):
    '''
    def writes global attributes (metadata) to newly created netCDF
    '''
    for key in config_dict['global_attrs'].keys():
        nc_rootgrp.__setattr__(key, config_dict['global_attrs'][key]) 


def netCDF_dimensions(nc_rootgrp, config_dict, logger):
    '''
    reads dimensions from yaml config file and writes them to netCDF
    '''
    for key in config_dict['dimensions'].keys():
        logger.info(msg=f'creating netCDF dimension: {key}')
        nc_rootgrp.createDimension(key, config_dict['dimensions'][key]['size'])


def set_netcdf_variable(key, one_var_dict, nc_group, timestamp, logger):
    logger.info(msg=f"creating netCDF variable {one_var_dict['var_attrs']['standard_name']}")
    # print(one_var_dict)
    if one_var_dict['include_in_nc'] is True:  # one_var_dict['include_in_nc'] is True:

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
            variable = nc_group.createVariable(one_var_dict['var_attrs']['standard_name'], 
                                            one_var_dict['dtype'],
                                            tuple([dim for dim in one_var_dict['dimensions']]),
                                            compression=compression_method,
                                            fill_value=fill_val,
                                            )
        # fill predefine values
        if 'value' in one_var_dict.keys() and len(one_var_dict['value']) == 1:
            # use .assignValue() method for scalar values
            variable.assignValue(one_var_dict['value'])  
        elif 'value' in one_var_dict.keys() and len(one_var_dict['value']) > 1:
            variable[:] = one_var_dict['value']

        for var_attr in one_var_dict['var_attrs']:
            variable.__setattr__(var_attr, one_var_dict['var_attrs'][var_attr]) 
        if key == 'time':
            variable.__setattr__('units', f'hours since {timestamp.strftime("%Y-%m-%d %H:%M:%S")} +00:00')


def netCDF_variables(nc_rootgrp, config_dict, timestamp, logger):
    '''
    Reads variables' definition from yaml config file and writes them to netCDF
    If variable values are set in the yml file def also assigns them their value
    '''
    # variables not in telegram
    for key, var_dict in config_dict['variables'].items():
        set_netcdf_variable(key=key, one_var_dict=var_dict, nc_group=nc_rootgrp, timestamp=timestamp, logger=logger)
        
    for key,var_dict in config_dict['telegram_fields'].items():
        set_netcdf_variable(key=key, one_var_dict=var_dict, nc_group=nc_rootgrp, timestamp=timestamp, logger=logger)

def join_f61_items(telegram_list):
    '''
    def uses the telegram_list index, of where F61 is positioned
    to mark th start of F61 items in telegram_list.
    Those items (with exception iog last, empty item) are return in the list of string f61_items

    Each one of the f61_items will be a row, with 2 columns (3 if we include timestamp).
    '''
    for index, item in enumerate(telegram_list):
        if 'F61:' in item.decode('utf-8', errors='replace'):
            f61_items = telegram_list[index:-1]  
            f61_items = [item.decode('utf-8', errors='replace').replace('\r\n', '').replace('F61:','') for item in f61_items]
            f61_items = f61_items
    return f61_items


def string2row(valuestr, delimiter, prefix):
    '''
    Converts a telegram string to a list of values, separated by the delimiter 
    and added timestamp to first item.
    '''
    values_list = (valuestr.replace(f'{prefix}:', '')).split(delimiter)        
    if values_list[-1] == '' or values_list[-1] == '\n':
        values_list = values_list[:-1]  
    return values_list


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
    # TODO: handle str to float|int conversion: if there is no A-z letter, and only numbers and . it is number
        # FIND DTYPE WHICH ARE USED TO INSERT TO NETCDF
        # can the val items be strs? How do they get converted to int|float before be inserred to netcdf?

