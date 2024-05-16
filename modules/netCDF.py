"""
netCDF export functionality class
"""
import os
import subprocess
from datetime import datetime
from venv import logger
from logging import Logger
from pathlib import Path
from typing import List, Dict, Union
import numpy
from cftime import date2num
from netCDF4 import Dataset # pylint: disable=no-name-in-module

class NetCDF:
    """
    class containing the netCDF export functionality
    """
    def __init__(self, logger: Logger, config_dict: Dict, data_dir: Path, fn_start: str, full_version, # pylint: disable=redefined-outer-name
                 telegram_objs: List[Dict],
                 date: datetime) -> None:
        self.logger = logger
        self.config_dict = config_dict
        self.data_dir = data_dir
        self.fn_start = fn_start
        self.date_dt = date
        self.telegram_objs = telegram_objs
        self.full_version = full_version
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
        for key in self.telegram_objs[0].telegram_data.keys(): # pylint: disable=too-many-nested-blocks
            if key in self.config_dict['telegram_fields'].keys() and \
                    ((self.full_version is True and self.config_dict['telegram_fields'][key].get('include_in_nc') != 'never') or
                    (self.full_version is False and self.config_dict['telegram_fields'][key].get('include_in_nc') == 'full')):
                field_dict = self.config_dict['telegram_fields'][key]
                standard_name = field_dict['var_attrs']['standard_name']
                netCDF_var = netCDF_rootgrp.variables[standard_name]

                # import pdb; pdb.set_trace()

                nc_details = (f'Handling values from NetCDF var: {key}, {netCDF_var.standard_name},'
                              f' {netCDF_var.dtype}, {netCDF_var._vltype}, {netCDF_var._isvlen},' # pylint: disable=protected-access
                              f' dims: {netCDF_var._getdims()}')  # pylint: disable=W0212
                logger.debug(msg=nc_details)

                if netCDF_var.dtype == str:  # S4
                    # assuming S4 vars are only 1D - that's the case for parsivel
                    self.__netcdf_populate_s4_var(netCDF_var_=netCDF_var,
                                                  var_key_=key)
                else:
                    if len(netCDF_var._getdims()) <= 2: # pylint: disable=protected-access
                        all_items_val = [telegram_obj.telegram_data[key] for telegram_obj in self.telegram_objs]
                        netCDF_var[:] = all_items_val
                    elif len(netCDF_var._getdims()) > 2 and key == '93': # pylint: disable=protected-access
                        all_f93_items_val = []

                        for telegram_obj in self.telegram_objs:
                            try:
                                assert len(telegram_obj.telegram_data[key]) == 1024,\
                                    'telegram_obj.telegram_data["93"] len != 1024'
                            except AssertionError as error:
                                self.logger.error(msg=f'DB item {telegram_obj.db_row_id}'
                                                      f' from {telegram_obj.timestamp} {error}'
                                                      f'. 32x32 ndarray with (error value)'
                                                      f' -9.999 will be added instead')
                                error_f93 = numpy.full(shape=(32, 32), fill_value='-9999', dtype='<U3')
                                all_f93_items_val.append(error_f93)
                            else:
                                reshaped_f93 = numpy.array(telegram_obj.telegram_data[key]).reshape(32, 32)
                                all_f93_items_val.append(reshaped_f93)
                                self.logger.debug(msg=f'F93 values from DB item {telegram_obj.db_row_id}'
                                                      f' from {telegram_obj.timestamp} successfully reshaped')

                        netCDF_var[:] = all_f93_items_val

        netCDF_rootgrp.close()
        self.logger.info(msg='class NetCDF executed write_data_to_netCDF()')

    def compress(self):
        """
        def compress
        """
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
        self.path_netCDF = self.data_dir / f'{self.fn_start}.nc' # pylint: disable=attribute-defined-outside-init
        self.path_netCDF_temp = self.data_dir / f'tmp_{self.fn_start}.nc' # pylint: disable=attribute-defined-outside-init

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
        if ((self.full_version is True and self.config_dict['telegram_fields'][key].get('include_in_nc') != 'never') or
            (self.full_version is False and self.config_dict['telegram_fields'][key].get('include_in_nc') == 'full')):
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
                    list(one_var_dict['dimensions']),
                    # tuple([dim for dim in one_var_dict['dimensions']]), - previous
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
                variable.__setattr__(var_attr, one_var_dict['var_attrs'][var_attr]) # pylint: disable=unnecessary-dunder-call
            if key == 'time':
                _start_dt = self.date_dt.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
                variable.__setattr__('units', f'hours since {_start_dt} +00:00') # pylint: disable=unnecessary-dunder-call

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
            nc_rootgrp.__setattr__(key, self.config_dict['global_attrs'][key]) # pylint: disable=unnecessary-dunder-call


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
