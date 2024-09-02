"""
Module for testing export_disdrodlDB2NC.py.

The aim of this module is to test whether the script functions as a whole,
not to test whether individual funcionalities are correct.
That is mainly done in test_db.py.

Functions:
- side_effect: Side effect to replace 'data_dir' in mocked netCDF objects.
"""

import os
import unittest
import logging
from pathlib import Path
from logging import StreamHandler
from datetime import datetime, timezone
from unittest.mock import patch, Mock
import pytest
from netCDF4 import Dataset
import export_disdrodlDB2NC
from modules.util_functions import create_dir
from modules.sqldb import connect_db
from modules.netCDF import NetCDF

output_file_dir = Path('sample_data/')
db_path_thies = output_file_dir / 'test_thies.db'
db_path_parsivel = output_file_dir / 'test_parsivel.db'

start_dt = datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)

log_handler = StreamHandler()
logger = logging.getLogger('test-log')
logger.addHandler(log_handler)


def side_effect(*args, **kwargs):
    """
    Side effect to replace 'data_dir' in mocked netCDF objects.
    :return: netCDF instance with substituted 'data_dir'
    """
    kwargs['data_dir'] = output_file_dir
    instance = NetCDF(*args, **kwargs)
    instance.logger = Mock()
    return instance

@pytest.mark.usefixtures("db_insert_24h_parsivel")
class ExportParsivelTests(unittest.TestCase):
    """
    Class for testing export_disdrodlDB2NC.py for the Parsivel.

    Functions:
    - test_parsivel_full: Verifies that exporting a full version of the PAR008 sensor results in no errors.
    - test_parsivel_light: Verifies that exporting a light version of the PAR008 sensor results in no errors.
    """

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_parsivel_full(self, mock_NetCDF, mock_connect_db, mock_create_dir): # pylint: disable=unused-argument
        """
        This function verifies that exporting a full version of the PAR008 sensor results in no errors.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_PAR008.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_PAR_008_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_parsivel_light(self, mock_NetCDF, mock_connect_db, mock_create_dir): # pylint: disable=unused-argument
        """
        This function verifies that exporting a light version of the PAR008 sensor results in no errors.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_PAR008_light.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_PAR_008_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'light'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

@pytest.mark.usefixtures("db_insert_24h_thies")
class ExportThiesTests(unittest.TestCase):
    """
    Class for testing export_disdrodlDB2NC.py for the Thies.

    Functions:
    - test_thies_full: Verifies that exporting a full version of the THIES006 sensor results in no errors.
    - test_thies_light: Verifies that exporting a light version of the THIES006 sensor results in no errors.
    """

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_thies_full(self, mock_NetCDF, mock_connect_db, mock_create_dir): # pylint: disable=unused-argument
        """
        This function verifies that exporting a full version of the THIES006 sensor results in no errors.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_THIES006.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_THIES_006_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_thies.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_thies_light(self, mock_NetCDF, mock_connect_db, mock_create_dir): # pylint: disable=unused-argument
        """
        This function verifies that exporting a light version of the THIES006 sensor results in no errors.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_THIES006_light.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_THIES_006_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'light'

        db_path = Path("sample_data/test_thies.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        os.remove("sample_data/test_thies.db")

@pytest.mark.usefixtures("db_insert_24h_parsivel")
class ExportArgumentExceptionTests(unittest.TestCase):
    """
    This class contains tests for passing illegal arguments to export_disdrodlDB2NC.py.

    Functions:
    - test_bad_config: Verifies that passing an unrecognized config file as argument results in an error.
    - test_bad_date: Verifies that passing an incorrectly formatted date as argument results in an error.
    - test_bad_version: Verifies that passing an unrecognized version type as argument results in a SystemExit.
    """

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_bad_config(self, mock_NetCDF, mock_connect_db, mock_create_dir):
        """
        This function verifies that passing an unrecognized config file as argument results in an error.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_000.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        with self.assertRaises(FileNotFoundError):
            export_disdrodlDB2NC.main(mock_args)

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_bad_date(self, mock_NetCDF, mock_connect_db, mock_create_dir):
        """
        This function verifies that passing an incorrectly formatted date as argument results in an error.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_PAR_008_GV.yml'
        mock_args.date = '2024'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        with self.assertRaises(Exception):
            export_disdrodlDB2NC.main(mock_args)

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_bad_version(self, mock_NetCDF, mock_connect_db, mock_create_dir):
        """
        This function verifies that passing an unrecognized version type as argument results in a SystemExit.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_PAR008.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_PAR_008_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'bad'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        result = 0

        try:
            export_disdrodlDB2NC.main(mock_args)
        except SystemExit:
            result = 1

        assert result == 1
        assert output_file_path.exists() is False

@pytest.mark.usefixtures("db_insert_24h_empty_parsivel")
class EmptyExportTests(unittest.TestCase):
    """
    This class contains tests for running export_disdrodlDB2NC.py for a date with no database entries.

    Functions:
    - test_no_telegrams: Verifies that running the export script for a date
        without database entries resuls in a SystemExit.
    """

    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_no_telegrams(self, mock_NetCDF, mock_connect_db, mock_create_dir):
        """
        This function verifies that running the export script for a date
        without database entries resuls in a SystemExit.
        :param mock_NetCDF: Mock object for NetCDF objects
        :param mock_connect_db: Mock object for connecting to the test database with connect_db
        :param mock_create_dir: Mock object for creating the output directory
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_PAR008.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_PAR_008_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_create_dir.return_value = create_dir(path=output_file_dir)

        mock_NetCDF.side_effect = side_effect

        result = 0
        try:
            export_disdrodlDB2NC.main(mock_args)
        except SystemExit:
            result = 1

        assert result == 1
        assert output_file_path.exists() is False

        os.remove("sample_data/test_parsivel.db")


@pytest.mark.usefixtures("db_insert_24h_w_empty_telegram_parsivel")
class MissingDataExportTests(unittest.TestCase):
    """
    Class tests  export_disdrodlDB2NC.py handling of DB with empty telegrams

    Functions:
    - test_NetCDF_export_w_gaps_parsivel: Verifies that running the export script for a date
        without database entries resuls in a SystemExit.
    """
    @patch('export_disdrodlDB2NC.create_dir')
    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_NetCDF_export_w_gaps_parsivel(self, mock_NetCDF, mock_connect_db, mock_create_dir):
        output_file_path = output_file_dir / '20240101_Test_Suite-TEST_PAR000.nc'  # see configs_netcdf/config_PAR_000_TEST.yml
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        test_db_path_str = 'sample_data/test_parsivel.db'
        test_db_path = Path(test_db_path_str)
        data_points_24h = 1440  # (60min * 24h)
        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_PAR_000_TEST.yml'  # db_path sample_data/test_parsivel.db
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'
        mock_connect_db.return_value = connect_db(dbpath=str(test_db_path))
        mock_create_dir.return_value = create_dir(path=output_file_dir)
        mock_NetCDF.side_effect = side_effect
        export_disdrodlDB2NC.main(mock_args)

        # test netcdf:  only half of data points should have be included
        assert output_file_path.exists()
        rootgrp = Dataset(output_file_path, 'r', format="NETCDF4")
        netCDF_var_time = rootgrp.variables['time']
        netCDF_var_time_data = netCDF_var_time[:].data
        assert len(netCDF_var_time_data) == data_points_24h / 2
        netCDF_var_tsensor = rootgrp.variables['T_sensor']
        netCDF_var_tsensor_data = netCDF_var_tsensor[:].data
        assert len(netCDF_var_tsensor_data) == data_points_24h / 2
        assert netCDF_var_tsensor_data[0] == 21 and netCDF_var_tsensor_data[1] == 21

        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        os.remove(test_db_path)

# TODO: same with thies

