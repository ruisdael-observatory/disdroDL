import csv
import os
from datetime  import datetime, timedelta
from netCDF4 import Dataset, stringtochar
from modules.util_functions import capture_telegram_prfx_vars
from pprint import pprint
from cftime import date2num, num2date
import numpy
import random

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
    Class dedicated to handling the returned telegram lines:
        storing, processing and writing to CSV
    Note: f61 is handled a little differently as its values are multi-line, hence self.f61_rows
    
    Methods:
        * create_csv_headers()
        * capture_prefixes_and_data()
        * append_data_to_csv()
    '''
    def __init__(self, telegram_lines, timestamp, data_dir, data_fn_start):
        self.telegram_lines = telegram_lines
        self.timestamp = timestamp  # change to self.timestamp_str
        self.timestamp_datetime = datetime.fromisoformat(self.timestamp) 
        self.svfs_values = None
        self.svfs_headers = []
        self.f90_values = None
        self.f91_values = None
        self.f93_values = None
        self.f61_values = None
        self.f61_rows = []
        self.f61_headers = []
        self.delimiter = ';'
        self.data_dir = data_dir  
        self.path_netCDF = None
        self.data_fn_start = data_fn_start 
        # data_fn_start shared filename start str, based on date_location_parsivelcode_
        # ie. 20230221_Delft-GV_PAR008_  *.csv

    def create_csv_headers(self, sfvs_telegram_resquest, config_dict):
        '''def Creates the headers to CSV of F61 and SVFS
            config.yml telegram_fields name and unit are used
            adds them to self.f61_headers & self.svfs_headers variables
        '''
        # SVFS
        headers_numbers = ((sfvs_telegram_resquest.replace('%','')).split(';'))[:-1]
        headers_names = []
        for key in headers_numbers:
            header = f"{config_dict['telegram_fields'][key]['var_attrs']['long_name']}"
            if 'unit' in config_dict['telegram_fields'][key].keys():
                header = f"{header} ({config_dict['telegram_fields'][key]['var_attrs']['units']})"
            headers_names.append(header)
        self.svfs_headers = ['timestamp'] + headers_names 
        # F61
        self.f61_headers = [
            'timestamp',
            f"{config_dict['telegram_fields']['61size']['name']} ({config_dict['telegram_fields']['61size']['unit']})",
            f"{config_dict['telegram_fields']['61speed']['name']} ({config_dict['telegram_fields']['61speed']['unit']})"
            ]                    

    def capture_prefixes_and_data(self):
        '''
        def Captures the prefixes and data returned by telegram
        and adds data to appropriate (determined by prefix) self.*_values variable.
        '''
        for telegram_line in self.telegram_lines:
            prefix, values = capture_telegram_prfx_vars(telegram_line=telegram_line)
            if prefix and len(values) > 1 and prefix == 'F61':  # len(values) > 1 since ";" can be captured without values
                self.f61_values = join_f61_items(telegram_list=self.telegram_lines)
                for f61_item in self.f61_values:
                    f61_item_pair = string2row(timestamp=self.timestamp, valuestr=f61_item, delimiter=self.delimiter, prefix=prefix)
                    self.f61_rows.append(f61_item_pair) 
            elif prefix in ['SVFS', 'F90', 'F91', 'F93'] and values:
                prefix_lcase = prefix.lower()
                super(Telegram, self).__setattr__(f'{prefix_lcase}_values', 
                                                  string2row(timestamp=self.timestamp, valuestr=values, delimiter=self.delimiter, prefix=prefix))
    def append_data_to_csv(self, prefix):
        '''
        def Writes headers and appends data from self.*_values to corresponding CSV
        using the self.data_dir and prefix to construct the path + file name.
        In cases of multiline values (F61) several rows are written
        '''
        prefix_lcase = prefix.lower()
        fn = f'{self.data_fn_start}_{prefix}.csv' # TODO: move var assignment to __init__
        # write headers to csv
        if f'{prefix_lcase}_headers' in self.__dir__() and not os.path.exists(self.data_dir / fn):
            # if headers variable exists and file does not exist
            with open(self.data_dir / fn, "w") as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                writer.writerow(self.__dict__[f'{prefix_lcase}_headers'])
        # write data
        if prefix == 'F61':
            data = self.__dict__[f'{prefix_lcase}_rows']
        else: 
            data = self.__dict__[f'{prefix_lcase}_values']  # prefix will determine what var will be used
        if len(data) > 0:  # prevent empty data to be written
            with open(self.data_dir / fn, "a") as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                if type(data[0]) == list:
                    for data_item in data:
                        writer.writerow(data_item)
                elif type(data[0]) == str:
                    writer.writerow(data)

    def create_netCDF(self, config_dict):
        '''
        def creates new netCDF file with dimensions and global attributes
        '''
        self.path_netCDF = self.data_dir / f'{self.data_fn_start}.nc' # TODO: move var assignment to __init__
        if not os.path.exists(self.path_netCDF):
            netCDF_rootgrp = Dataset(self.path_netCDF, "w", format="NETCDF4")
            global_attrs_to_netCDF(nc_rootgrp=netCDF_rootgrp, config_dict=config_dict)
            netCDF_dimensions(nc_rootgrp=netCDF_rootgrp, config_dict=config_dict)
            netCDF_variables(nc_rootgrp=netCDF_rootgrp, config_dict=config_dict, todaysdateobj=self.timestamp_datetime)
            netCDF_rootgrp.close()
    
    def append_data_to_netCDF(self, now_time_obj):
        '''
        appends data to netCDF
        DONE: time
        TODO: other parameters
        '''
        self.path_netCDF = self.data_dir / f'{self.data_fn_start}.nc'  # TODO: move var assignment to __init__
        netCDF_rootgrp = Dataset(self.path_netCDF, "a", format="NETCDF4")
        # netCDF_rootgrp.set_fill_off()
        
        # (time) appending timestamps to var time
        netCDF_var_time = netCDF_rootgrp.variables['time']
        time_now_array = date2num([now_time_obj], units=netCDF_var_time.units,calendar=netCDF_var_time.calendar)
        netCDF_var_time[:] = numpy.concatenate([netCDF_var_time[:].data, time_now_array])
        print('netCDF_var_time:', netCDF_var_time, netCDF_var_time[:].data )
        currentindex = len(netCDF_var_time[:].data) - 1

        # (temp) append rain_intensity 
        netCDF_var_ri = netCDF_rootgrp.variables['rain_intensity']
        random_val = float(random.random())
        netCDF_var_ri[currentindex] = random_val 

        # (temp) append synop_waw (code_4680)
        netCDF_var_synop_waw = netCDF_rootgrp.variables['code_4680']
        random_val = random.choice([00, 20, 54])
        netCDF_var_synop_waw[currentindex] = random_val
        
        # print('concat:', netCDF_var_ri[:].data, [random_val],numpy.concatenate([netCDF_var_ri[:].data, [random_val]]) )
        # print('netCDF_var_ri[:].data',netCDF_var_ri[:].data)
        # netCDF_var_ri[:] =  numpy.append( netCDF_var_ri[:].data, values=[random_val])
        netCDF_rootgrp.close()
       

def global_attrs_to_netCDF(nc_rootgrp, config_dict):
    '''
    def writes global attributes (metadata) to newly created netCDF
    '''
    for key in config_dict['global_attrs'].keys():
        nc_rootgrp.__setattr__(key, config_dict['global_attrs'][key]) 

def netCDF_dimensions(nc_rootgrp, config_dict):
    '''
    reads dimensions from yaml config file and writes them to netCDF
    '''
    for key in config_dict['dimensions'].keys():
        print('dimension:', key)
        nc_rootgrp.createDimension(key, config_dict['dimensions'][key]['size'])

def set_netcdf_variable(key, one_var_dict, nc_group, todaysdateobj):
    print(key, one_var_dict, one_var_dict['dimensions'])
    if one_var_dict['dimensions'] == None:
        # scalar variables do not use dimensions
        variable = nc_group.createVariable(one_var_dict['var_attrs']['standard_name'], 
                                                one_var_dict['dtype'],)
        variable.assignValue(one_var_dict['value'])
    elif len(one_var_dict['dimensions']) == 1:
        variable = nc_group.createVariable(one_var_dict['var_attrs']['standard_name'], 
                                                one_var_dict['dtype'],
                                                tuple([dim for dim in one_var_dict['dimensions']])
                                                )               
    for var_attr in one_var_dict['var_attrs']:
        variable.__setattr__(var_attr, one_var_dict['var_attrs'][var_attr])
    if  key == 'time':
        # TODO: replace YYYY for current date
        variable.__setattr__('units', f'hours since {todaysdateobj.strftime("%Y-%m-%d")} 00:00:00 +00:00')
    # print('value:', one_var_dict['value'])


def netCDF_variables(nc_rootgrp, config_dict, todaysdateobj):
    '''
    Reads variables' definition from yaml config file and writes them to netCDF
    If variable values are set in the yml file def also assigns them their value
    '''
    # variables not in telegram
    for key in config_dict['variables'].keys():
        set_netcdf_variable(key=key, one_var_dict=config_dict['variables'][key], nc_group=nc_rootgrp, todaysdateobj=todaysdateobj)

    for key in config_dict['telegram_fields'].keys():
        set_netcdf_variable(key=key, one_var_dict=config_dict['telegram_fields'][key], nc_group=nc_rootgrp, todaysdateobj=todaysdateobj)


def join_f61_items(telegram_list):
    '''
    def uses the telegram_list index, of where F61 is positioned
    to mark th start of F61 items in telegram_list.
    Those items (with exception iog last, empty item) are return in the list of string f61_items

    Each one of the f61_items will be a row, with 2 columns (3 if we include timestamp).
    '''
    for index, item in enumerate(telegram_list):
        if 'F61:' in item.decode('utf-8'):
            f61_items = telegram_list[index:-1]  
            f61_items = [item.decode('utf-8').replace('\r\n', '').replace('F61:','') for item in f61_items]
            f61_items = f61_items
    return f61_items

def string2row(timestamp, valuestr, delimiter, prefix):
    '''
    Converts a telegram string to a list of values, separated by the delimiter 
    and added timestamp to first item.
    The output is ready to be written to CSV 
    '''
    values_list = (valuestr.replace(f'{prefix}:', '')).split(delimiter)        
    values_list = [timestamp] + values_list
    if values_list[-1] == '' or values_list[-1] == '\n':
        values_list = values_list[:-1]  
    return values_list



if __name__ == '__main__':
    now = NowTime()
    print(now.__doc__)
    print(now, now.__dict__, now.utc, now.time_list)
    print(type(now.utc))
    now.date_strings()
    print(now.ymd)
    print(type(now.iso))


