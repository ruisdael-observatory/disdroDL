"""
Module for testing export_disdrodlDB2NC.py.

The aim of this module is to test whether the script functions as a whole,
not to test whether individual funcionalities are correct.
That is mainly done in test_db.py.
"""

import subprocess
import sys
import os
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, call, MagicMock
import pytest
import export_disdrodlDB2NC
from modules.sqldb import query_db_rows_gen, connect_db
from modules.netCDF import NetCDF

env = os.environ.copy()
standard_args = [sys.executable]

output_file_dir = Path('sample_data/')
data_dir_substitute = Path('sample_data/')

def side_effect(*args, **kwargs):
    kwargs['data_dir'] = data_dir_substitute
    instance = NetCDF(*args, **kwargs)
    instance.logger = Mock()
    return instance

@pytest.mark.usefixtures("db_insert_24h_parsivel")
class ExportParsivelTests(unittest.TestCase):
    """
    Class for testing export_disdrodlDB2NC.py for the Parsivel
    """

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_parsivel_full(self, mock_NetCDF, mock_connect_db): # pylint: disable=unused-argument
        """
        This function verifies that exporting a full version of the PAR008 sensor results in no errors
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

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_parsivel_light(self, mock_NetCDF, mock_connect_db): # pylint: disable=unused-argument
        """
        This function verifies that exporting a light version of the PAR008 sensor results in no errors
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

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)
            
@pytest.mark.usefixtures("db_insert_24h_thies")
class ExportThiesTests(unittest.TestCase):
    """
    Class for testing export_disdrodlDB2NC.py for the Thies
    """

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_thies_full(self, mock_NetCDF, mock_connect_db): # pylint: disable=unused-argument
        """
        This function verifies that exporting a full version of the THIES006 sensor results in no errors
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_THIES006.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_008_GV_THIES.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_thies.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_thies_light(self, mock_NetCDF, mock_connect_db): # pylint: disable=unused-argument
        """
        This function verifies that exporting a light version of the THIES006 sensor results in no errors
        """
        output_file_path = output_file_dir / '20240101_Green_Village-GV_THIES006_light.nc'

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_008_GV_THIES.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'light'

        db_path = Path("sample_data/test_thies.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_NetCDF.side_effect = side_effect

        export_disdrodlDB2NC.main(mock_args)

        assert output_file_path.exists()

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

@pytest.mark.usefixtures("db_insert_24h_parsivel")
class ExportArgumentExceptionTests(unittest.TestCase):
    """
    This class contains tests for passing illegal arguments to export_disdrodlDB2NC.py
    """

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_bad_config(self, mock_NetCDF, mock_connect_db):
        """
        This function verifies that passing an unrecognized config file as argument results in an error
        """
        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_000.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_NetCDF.side_effect = side_effect

        with self.assertRaises(Exception):
            export_disdrodlDB2NC.main(mock_args)

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_bad_date(self, mock_NetCDF, mock_connect_db):
        """
        This function verifies that passing an incorrectly formatted date as argument results in an error
        """
        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
        mock_args.date = '2024'
        mock_args.version = 'full'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_NetCDF.side_effect = side_effect

        with self.assertRaises(Exception):
            export_disdrodlDB2NC.main(mock_args)

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_bad_version(self, mock_NetCDF, mock_connect_db):
        """
        This function verifies that passing an unrecognized version type as argument results in an error
        """
        mock_args = Mock()
        mock_args.config = 'configs_netcdf/config_008_GV.yml'
        mock_args.date = '2024-01-01'
        mock_args.version = 'bad'

        db_path = Path("sample_data/test_parsivel.db")
        mock_connect_db.return_value = connect_db(dbpath=str(db_path))

        mock_NetCDF.side_effect = side_effect

        result = 0

        try:
            export_disdrodlDB2NC.main(mock_args)
        except SystemExit:
            result = 1

        assert result == 1

@pytest.mark.usefixtures("db_insert_24h_empty_parsivel")
class EmptyExportTests(unittest.TestCase):
    """
    This class contains tests for running export_disdrodlDB2NC.py for a date with no database entries
    """

    @patch('export_disdrodlDB2NC.connect_db')
    @patch('export_disdrodlDB2NC.NetCDF')
    def test_no_telegrams(self, mock_NetCDF, mock_connect_db):
        """
        This function verifies that running the export script for a date without database entries resuls in an error
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

        mock_NetCDF.side_effect = side_effect

        result = 0

        try:
            export_disdrodlDB2NC.main(mock_args)
        except SystemExit:
            result = 1

        assert result == 1
        assert output_file_path.exists() == False

        if os.path.exists(output_file_path):
            os.remove(output_file_path)
