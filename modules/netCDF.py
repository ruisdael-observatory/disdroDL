"""
This file contains the netCDF class and functions for creating,writing to and compressing
netCDFs for the Parsivel and Thies optical disdrometers.


Functions:
- unpack_telegram_from_db: unpacks telegram string from sqlite DB row into a dictionary
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
from netCDF4 import Dataset  # pylint: disable=no-name-in-module


class NetCDF:
    """
    Class containing the netCDF export functionality.

    Attributes:
    - logger: logger object for logging info related to the netCDF object
    - config_dict: a combined site specific and sensor type specific config file
    - data_dir: directory for the netCDF file
    - fn_start: file name for the netCDF file
    - full_version: bool to indicate whether this netCDF is a full or light version
    - telegram_objs: list with all telegram objects
    - date_dt: the date from when the data is
    - path_netCDF: full path for the netCDF file
    - path_netCDF_temp: additional temporary path for the netCDF file

    Functions:
    - create_netCDF: creates a new netCDF file
    - write_data_to_netCDF_thies: writes data from ThiesTelegram objects to the netCDF file
    - write_data_to_netCDF_parsivel: writes data from ParsivelTelegram objects to the netCDF file
    - compress: compresses the netCDF file
    - __set_netCDF_path: sets the path of the netCDF based on fn_start
    - __netcdf_populate_s4_var: populates netCDF S4 vars
    - __netcdf_variables: reads variables' definition from yaml config file and writes them to netCDF
    - __set_netcdf_variable: sets the value for a specific variable in the netCDF
    - __netCDF_dimensions: reads dimensions from yaml config file and writes them to netCDF
    - __global_attrs_to_netCDF: writes global attributes to newly created netCDF
    """

    def __init__(self, logger: Logger, config_dict: Dict, data_dir: Path, fn_start: str, full_version,
                 # pylint: disable=redefined-outer-name
                 telegram_objs: List[Dict],
                 date: datetime) -> None:
        """
        Constructor for NetCDF.
        """
        self.logger = logger
        self.config_dict = config_dict
        self.data_dir = data_dir
        self.fn_start = fn_start
        self.date_dt = date
        self.telegram_objs = telegram_objs
        self.full_version = full_version
        logger.debug(msg="NetCDF class is initialized")

    def create_netCDF(self):
        """
        This function creates new netCDF file with global attributes, dimensions and variables (defined in yaml).
        """
        self.__set_netCDF_path()
        netCDF_rootgrp = Dataset(self.path_netCDF, "w", format="NETCDF4")
        self.__global_attrs_to_netCDF(nc_rootgrp=netCDF_rootgrp)
        self.__netCDF_dimensions(nc_rootgrp=netCDF_rootgrp)
        self.__netcdf_variables(nc_rootgrp=netCDF_rootgrp)
        netCDF_rootgrp.close()
        self.logger.info(msg='class NetCDF executed create_netCDF()')

    def write_data_to_netCDF_thies(self):
        """
        This function writes data from self.telegram_objs, containing ThiesTelegram objects, to the netCDF file.
        """
        netCDF_rootgrp = Dataset(self.path_netCDF, "a", format="NETCDF4")

        # --- NetCDF variables NOT in telegram_data ---

        # var: time - appending timestamps to var time
        # this part adds the time to th netcdf
        netCDF_var_time = netCDF_rootgrp.variables['time']
        value_list_dt = [telegram_obj.timestamp for telegram_obj in self.telegram_objs]
        time_value_list = [date2num(timestamp_val, units=netCDF_var_time.units, calendar=netCDF_var_time.calendar)
                           for timestamp_val in value_list_dt]
        netCDF_var_time[:] = time_value_list  # numpy.concatenate([netCDF_var_time[:].data, time_now_array])

        # NetCDF var: datetime (iso str values)
        netCDF_var_datetime = netCDF_rootgrp.variables['datetime']
        self.__netcdf_populate_s4_var(netCDF_var_=netCDF_var_datetime, var_key_='timestamp')

        # --- NetCDF variables in telegram_data ---
        for key in self.telegram_objs[0].telegram_data.keys():  # pylint: disable=too-many-nested-blocks

            # checks if key is not in the telegram fields or if the value from the telegram should not be added
            # to the netcdf (either should never be added or a light netcdf has been requested), if that is the
            # case go onto next key
            if key not in self.config_dict['telegram_fields'].keys() or \
                    ((self.full_version is True and
                      self.config_dict['telegram_fields'][key].get('include_in_nc') == 'never') or
                     (self.full_version is False and
                      self.config_dict['telegram_fields'][key].get('include_in_nc') != 'always')):
                continue

            field_dict = self.config_dict['telegram_fields'][key]
            standard_name = field_dict['var_attrs']['standard_name']
            netCDF_var = netCDF_rootgrp.variables[standard_name]

            # import pdb; pdb.set_trace()
            # message for the debugger
            nc_details = (f'Handling values from NetCDF var: {key}, {netCDF_var.standard_name},'
                          f' {netCDF_var.dtype}, {netCDF_var._vltype}, {netCDF_var._isvlen},'  # pylint: disable=protected-access
                          f' dims: {netCDF_var._getdims()}')  # pylint: disable=W0212
            logger.debug(msg=nc_details)

            # check that the value in the key value pair is supposed to be of type string,
            # if so use function for populating strings
            if netCDF_var.dtype == str:  # S4
                # assuming S4 vars are only 1D
                self.__netcdf_populate_s4_var(netCDF_var_=netCDF_var,
                                              var_key_=key)
            else:

                # check that the variable has 2 or fewer dimensions and if so add to netCDF
                if len(netCDF_var._getdims()) <= 2:  # pylint: disable=protected-access
                    all_items_val = [telegram_obj.telegram_data[key] for telegram_obj in self.telegram_objs]
                    netCDF_var[:] = all_items_val

                # check if variable has more than 2 dimensions and the key
                # associated with the key:value pair is 81 (only 3D variable in Thies telegram)
                elif len(netCDF_var._getdims()) > 2 and key == '81':  # pylint: disable=protected-access
                    all_f81_items_val = []

                    for telegram_obj in self.telegram_objs:
                        try:
                            # value associated with key 81 is supposed to be a list of 440
                            # values representing particle diameter and velocity classes
                            # this is later converted to a 22x20 matrix
                            # checks if the value is a list of length 440
                            assert len(telegram_obj.telegram_data[key]) == 440, \
                                'telegram_obj.telegram_data["81"] len == 440'
                        except AssertionError as error:
                            self.logger.error(msg=f'DB item {telegram_obj.db_row_id}'
                                                  f' from {telegram_obj.timestamp} {error}'
                                                  f'. 22x20 ndarray with (error value)'
                                                  f' -99 will be added instead')
                            # fills fields with default -99 error value if error has occurred
                            error_f81 = numpy.full(shape=(22, 20), fill_value='-99', dtype='<U3')
                            all_f81_items_val.append(error_f81)
                        else:
                            # if list was of appropriate size reshapes it into a 22x20 matrix
                            reshaped_f81 = numpy.array(telegram_obj.telegram_data[key]).reshape(22, 20)
                            all_f81_items_val.append(reshaped_f81)
                            self.logger.debug(msg=f'F81 to F520 values from DB item {telegram_obj.db_row_id}'
                                                  f' from {telegram_obj.timestamp} successfully reshaped')

                    netCDF_var[:] = all_f81_items_val

        netCDF_rootgrp.close()
        self.logger.info(msg='class NetCDF executed write_data_to_netCDF()')

    def write_data_to_netCDF_parsivel(self):
        """
        This function writes data from self.telegram_objs, containing ParsivelTelegram objects, to the netCDF file.
        """
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
        for key in self.telegram_objs[0].telegram_data.keys():  # pylint: disable=too-many-nested-blocks

            # checks if key is not in the telegram fields or if the value from the telegram should not be added
            # to the netcdf (either should never be added or a light netcdf has been requested), if that is the
            # case go onto next key
            if not (key in self.config_dict['telegram_fields'].keys()) or \
                    ((self.full_version is True and
                      self.config_dict['telegram_fields'][key].get('include_in_nc') == 'never') or
                     (self.full_version is False and
                      self.config_dict['telegram_fields'][key].get('include_in_nc') != 'always')):
                continue

            field_dict = self.config_dict['telegram_fields'][key]
            standard_name = field_dict['var_attrs']['standard_name']
            netCDF_var = netCDF_rootgrp.variables[standard_name]

            # import pdb; pdb.set_trace()
            # message for the debugger
            nc_details = (f'Handling values from NetCDF var: {key}, {netCDF_var.standard_name},'
                          f' {netCDF_var.dtype}, {netCDF_var._vltype}, {netCDF_var._isvlen},'  # pylint: disable=protected-access
                          f' dims: {netCDF_var._getdims()}')  # pylint: disable=W0212
            logger.debug(msg=nc_details)

            # check that the value in the key value pair is supposed to be of type string,
            # if so use function for populating strings
            if netCDF_var.dtype == str:  # S4
                # assuming S4 vars are only 1D - that's the case for the parsivel
                self.__netcdf_populate_s4_var(netCDF_var_=netCDF_var,
                                              var_key_=key)
            else:

                # check that the variable has 2 or fewer dimensions and if so add to netCDF
                if len(netCDF_var._getdims()) <= 2:  # pylint: disable=protected-access
                    all_items_val = [telegram_obj.telegram_data[key] for telegram_obj in self.telegram_objs]
                    netCDF_var[:] = all_items_val


                elif len(netCDF_var._getdims()) > 2 and key == '93':  # pylint: disable=protected-access
                    all_f93_items_val = []

                    for telegram_obj in self.telegram_objs:
                        try:
                            # value associated with key 93 is supposed to be a list of 1024
                            # values, this is later converted to a 32x32 matrix
                            # checks if the value is a list of length 1024
                            assert len(telegram_obj.telegram_data[key]) == 1024, \
                                'telegram_obj.telegram_data["93"] len != 1024'
                        except AssertionError as error:
                            self.logger.error(msg=f'DB item {telegram_obj.db_row_id}'
                                                  f' from {telegram_obj.timestamp} {error}'
                                                  f'. 32x32 ndarray with (error value)'
                                                  f' -99 will be added instead')
                            # fills fields with default -99 error value if error has occurred
                            error_f93 = numpy.full(shape=(32, 32), fill_value='-99', dtype='<U3')
                            all_f93_items_val.append(error_f93)
                        else:
                            # if list was of appropriate size reshapes it into a 32x32 matrix
                            reshaped_f93 = numpy.array(telegram_obj.telegram_data[key]).reshape(32, 32)
                            all_f93_items_val.append(reshaped_f93)
                            self.logger.debug(msg=f'F93 values from DB item {telegram_obj.db_row_id}'
                                                  f' from {telegram_obj.timestamp} successfully reshaped')

                    netCDF_var[:] = all_f93_items_val

        netCDF_rootgrp.close()
        self.logger.info(msg='class NetCDF executed write_data_to_netCDF()')

    def compress(self):
        """
        This function compresses the netCDF file.
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
        """
        This function sets the path of the netCDF file based on self.fn_start.
        """
        self.path_netCDF = self.data_dir / f'{self.fn_start}.nc'  # pylint: disable=attribute-defined-outside-init
        self.path_netCDF_temp = self.data_dir /+ "/" + f'tmp_{self.fn_start}.nc'  # pylint: disable=attribute-defined-outside-init

    def __netcdf_populate_s4_var(self, netCDF_var_, var_key_):
        """
        This function populates the S4 vars of the netCDF file.
        In Python netCDF4 lib the dtype S4 (strings)
        are VLEN variables can only be assigned data
        one element at a time, with integer indices (not slices).
        :param netCDF_var_: netCDF variable object to be populated
        :param var_key_: key to get the data
        """
        # checks if variable is in telegram data
        if var_key_ in self.telegram_objs[0].telegram_data.keys():
            for i, telegram_obj in enumerate(self.telegram_objs):
                netCDF_var_[i] = telegram_obj.telegram_data[var_key_]
        else:
            # checks if variable is the time, if so convert to iso format
            # otherwise just add to netcdf
            if netCDF_var_.standard_name == 'datetime':
                for i, telegram_obj in enumerate(self.telegram_objs):
                    netCDF_var_[i] = getattr(telegram_obj, 'timestamp').isoformat()
            else:
                for i, telegram_obj in enumerate(self.telegram_objs):
                    netCDF_var_[i] = getattr(telegram_obj, var_key_)

    def __netcdf_variables(self, nc_rootgrp):
        """
        This function reads variables' definition from yaml config file and writes them to netCDF.
        If variable values are set in the yml file def also assigns them their value.
        :param nc_rootgrp: the root group of the netCDF file
        """
        # variables not in telegram and already given their values in the yml files
        for key, var_dict in self.config_dict['variables'].items():
            self.__set_netcdf_variable(key=key, one_var_dict=var_dict, nc_group=nc_rootgrp)
        # variables in telegram
        for key, var_dict in self.config_dict['telegram_fields'].items():
            self.__set_netcdf_variable(key=key, one_var_dict=var_dict, nc_group=nc_rootgrp)

    def __set_netcdf_variable(self, key, one_var_dict, nc_group):
        """
        This function sets the value for a specific variable in the netCDF.
        :param key: the key of the variable
        :param one_var_dict: the dict for the specific variable
        :param nc_group: the root group of the netCDF file
        """
        self.logger.info(msg=f"creating netCDF variable {one_var_dict['var_attrs']['standard_name']}")
        # checks if the value is supposed to be added
        if ((self.full_version is True and one_var_dict['include_in_nc'] != 'never') or
                (self.full_version is False and one_var_dict['include_in_nc'] == 'always')):
            # can't compress variable-length str variables
            if one_var_dict['dtype'] != 'S4':
                compression_method = 'zlib'
                # compression_method = dict(zlib=True, shuffle=True, complevel=5)
            else:
                compression_method = None

            if (one_var_dict['dtype'] == 'S4'):
                fill_val = ''
            else:
                fill_val = -999
            # compresses and adds values depending on if the variables are scalar or not
            if 'dimensions' not in one_var_dict.keys() or one_var_dict['dimensions'] is None:
                # scalar variables do not use dimensions
                variable = nc_group.createVariable(
                    one_var_dict['var_attrs']['standard_name'],
                    one_var_dict['dtype'],
                    fill_value=fill_val,
                    compression=compression_method,
                    complevel=9,
                    shuffle=True,
                    fletcher32=True)
            elif len(one_var_dict['dimensions']) >= 1:
                if 'fill_value' in one_var_dict.keys():
                    fill_val = one_var_dict['fill_value']

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
                variable.__setattr__(var_attr,
                                     one_var_dict['var_attrs'][var_attr])  # pylint: disable=unnecessary-dunder-call
            if key == 'time':
                _start_dt = self.date_dt.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
                variable.__setattr__('units',
                                     f'hours since {_start_dt} +00:00')  # pylint: disable=unnecessary-dunder-call

    def __netCDF_dimensions(self, nc_rootgrp):
        """
        This function reads dimensions from yaml config file and writes them to netCDF.
        :param nc_rootgrp: the root group of the netCDF file
        """
        for key in self.config_dict['dimensions'].keys():
            self.logger.info(msg=f'creating netCDF dimension: {key}')
            nc_rootgrp.createDimension(key, self.config_dict['dimensions'][key]['size'])

    def __global_attrs_to_netCDF(self, nc_rootgrp):
        """
        This function writes global attributes (metadata) to newly created netCDF.
        :param nc_rootgrp: the root group of the netCDF file
        """
        for key in self.config_dict['global_attrs'].keys():
            nc_rootgrp.__setattr__(key,
                                   self.config_dict['global_attrs'][key])  # pylint: disable=unnecessary-dunder-call


def unpack_telegram_from_db(telegram_str: str) -> Dict[str, Union[str, list]]:
    """
    This function unpacks telegram string from sqlite DB row into a dictionary.
    :param telegram_str: the root group of the netCDF file
    :return: the unpacked telegram dict

    * key precedes value NN:val
    * key:value pair, seperated by '; '
    * list: converted to str with ',' separator between values
    * empty lists, empty strings: converted to 'None'
    Example Input: '19:None; 20:10; 21:25.05.2023;
    51:000140; 90:-9.999,-9.999,-9.999,-9.999,-9.999 ...'
    Example Output:  {'60': '00000062', '90': '-9.999,-9.999,01.619,...'}
    """
    telegram_dict = {}
    # splits into key:value pairs
    telegram_list = telegram_str.split('; ')

    for telegram_item in telegram_list:
        # splits into keys and values using : as a delimiter
        key, val = telegram_item.split(':')
        if val == 'None':
            val = None
        # adds values to telegram dictionary
        telegram_dict[key] = val

    return telegram_dict
