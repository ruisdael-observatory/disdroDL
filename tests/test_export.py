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
from pathlib import Path
from unittest.mock import patch, Mock
import pytest
import export_disdrodlDB2NC
from modules.util_functions import create_dir
from modules.sqldb import connect_db
from modules.netCDF import NetCDF

output_file_dir = Path('sample_data/')

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
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
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
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
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
        mock_args.config = 'configs_netcdf/config_006_GV_THIES.yml'
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
        mock_args.config = 'configs_netcdf/config_006_GV_THIES.yml'
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
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
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
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
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
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
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
