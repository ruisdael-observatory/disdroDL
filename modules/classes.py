import os
from datetime  import datetime
from netCDF4 import Dataset
from cftime import date2num
import numpy
import chardet


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
    def __init__(self, config_dict, telegram_lines, timestamp, data_dir, data_fn_start, logger):
        '''
        initiates variables and methods:
        * set_netCDF_path
        * create_netCDF
        '''
        self.config_dict = config_dict
        self.telegram_lines = telegram_lines
        self.timestamp = timestamp
        self.delimiter = ';'
        self.data_dir = data_dir  
        self.data_fn_start = data_fn_start
        self.logger = logger
        self.path_netCDF = None
        self.set_netCDF_path()
        self.create_netCDF()
        self.telegram_data = {}

    def capture_prefixes_and_data(self):
        '''
        def Captures the telegram prefixes and data stored in self.telegram_lines
        and adds the data to self.telegram_data dict.
        '''
        for i in  self.telegram_lines:
            encoding = chardet.detect(i)['encoding']
            i_str = i.decode(encoding)
            i_list = i_str.split(":")
            if len(i_list) > 1 and i_list[1].strip() != self.delimiter:
                field = i_list[0]
                value = i_list[1].strip() # strip white space
                value_list = value.split(self.delimiter)
                value_list = [v for v in value_list if len(v) > 0]
                if len(value_list) == 1:
                    value = value_list[0]
                else:
                    value = value_list
                super(Telegram, self).__setattr__(f'field_{field}_values', value)
                self.telegram_data[field] = value


    def set_netCDF_path(self):
        self.path_netCDF = self.data_dir / f'{self.data_fn_start}.nc' 
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
            if key in self.config_dict['telegram_fields'].keys():
                field_dict = self.config_dict['telegram_fields'][key]
                standard_name = field_dict['var_attrs']['standard_name']
                netCDF_var = netCDF_rootgrp.variables[standard_name]
                # print(key,  '-- IN config_dict[telegram_fields] --',netCDF_var.standard_name )
                # print(key, netCDF_var.standard_name, standard_name, value)
                # print(type(value))
                if isinstance(value, str): #str
                    # print(f'str value: {value}')
                    netCDF_var[currentindex] = value
                elif isinstance(value, list): #str
                    # print(f'list value: {value}')
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
    if one_var_dict['dimensions'] == None:
        # scalar variables do not use dimensions
        variable = nc_group.createVariable( one_var_dict['var_attrs']['standard_name'], 
                                            one_var_dict['dtype'],
                                            fill_value=-1 #one_var_dict['fill_value'],
                                            )
        # variable.assignValue(one_var_dict['value'])
    elif len(one_var_dict['dimensions']) >= 1:
        variable = nc_group.createVariable(one_var_dict['var_attrs']['standard_name'], 
                                           one_var_dict['dtype'],
                                           tuple([dim for dim in one_var_dict['dimensions']]),
                                           fill_value=-1  # fill_value=one_var_dict['fill_value'],
                                           )
    # fill predefine values
    if 'value' in one_var_dict.keys() and len(one_var_dict['value']) == 1:
        # use .assignValue() method for scalar values
        variable.assignValue(one_var_dict['value'])  
    elif 'value' in one_var_dict.keys() and len(one_var_dict['value']) > 1:
        variable[:] = one_var_dict['value']

    for var_attr in one_var_dict['var_attrs']:
        variable.__setattr__(var_attr, one_var_dict['var_attrs'][var_attr])
    if  key == 'time':
        variable.__setattr__('units', f'hours since {timestamp.strftime("%Y-%m-%d")} 00:00:00 +00:00')
    # print('value:', one_var_dict['value'])



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

