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

env = os.environ.copy()
output_file_dir = Path('sample_data/')
standard_args = [sys.executable]

# Uncomment the line below to get coverage reports (run 'coverage combine' to combine them with the main report)
# standard_args = standard_args + ['-m', 'coverage', 'run', '--parallel-mode']

def test_parsivel_full():
    """
    This function verifies that exporting a full version of the PAR008 sensor results in no errors
    """
    output_file_path = output_file_dir / '20240101_Green_Village-GV_PAR008.nc'

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    env['MOCK_DB'] = '1'
    result = subprocess.run(
        standard_args +
        ['export_disdrodlDB2NC.py',
        '-c', 'configs_netcdf/config_008_GV.yml',
        '-d', '2024-01-01',
        '-v', 'full'],
        capture_output=True,
        check=True,
        env=env
    )

    assert result.returncode == 0
    assert output_file_path.exists()

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

def test_parsivel_light():
    """
    This function verifies that exporting a light version of the PAR008 sensor results in no errors
    """
    output_file_path = output_file_dir / '20240101_Green_Village-GV_PAR008_light.nc'

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    env['MOCK_DB'] = '1'
    result = subprocess.run(
        standard_args +
        ['export_disdrodlDB2NC.py',
        '-c', 'configs_netcdf/config_008_GV.yml',
        '-d', '2024-01-01',
        '-v', 'light'],
        capture_output=True,
        check=True,
        env=env
    )

    assert result.returncode == 0
    assert output_file_path.exists()

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

def test_thies_full():
    """
    This function verifies that exporting a full version of the THIES006 sensor results in no errors
    """
    output_file_path = output_file_dir / '20240513_Green_Village-GV_THIES006.nc'

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    env['MOCK_DB'] = '2'
    result = subprocess.run(
        standard_args +
        ['export_disdrodlDB2NC.py',
        '-c', 'configs_netcdf/config_008_GV_THIES.yml',
        '-d', '2024-05-13',
        '-v', 'full'],
        capture_output=True,
        check=True,
        env=env
    )

    assert result.returncode == 0
    assert output_file_path.exists()

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

def test_thies_light():
    """
    This function verifies that exporting a light version of the THIES006 sensor results in no errors
    """
    output_file_path = output_file_dir / '20240513_Green_Village-GV_THIES006_light.nc'

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    env['MOCK_DB'] = '2'
    result = subprocess.run(
        standard_args +
        ['export_disdrodlDB2NC.py',
        '-c', 'configs_netcdf/config_008_GV_THIES.yml',
        '-d', '2024-05-13',
        '-v', 'light'],
        capture_output=True,
        check=True,
        env=env
    )

    assert result.returncode == 0
    assert output_file_path.exists()

    if os.path.exists(output_file_path):
        os.remove(output_file_path)

class ExportExceptionTests(unittest.TestCase):
    """
    This class contains the bad weather tests for export_disdrodlDB2NC.py
    """

    def test_bad_config(self):
        """
        This function verifies that passing an unrecognized config file as argument results in an error
        """
        env['MOCK_DB'] = '1'
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(
                standard_args +
                ['export_disdrodlDB2NC.py',
                '-c', 'configs_netcdf/config_000.yml',
                '-d', '2024-01-01',
                '-v', 'full'],
                capture_output=True,
                check=True,
                env=env
            )

    def test_bad_date(self):
        """
        This function verifies that passing an incorrectly formatted date as argument results in an error
        """
        env['MOCK_DB'] = '1'
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(
                standard_args +
                ['export_disdrodlDB2NC.py',
                '-c', 'configs_netcdf/config_008_GV.yml',
                '-d', '2024',
                '-v', 'full'],
                capture_output=True,
                check=True,
                env=env
            )

    def test_bad_version(self):
        """
        This function verifies that passing an unrecognized version type as argument results in an error
        """
        env['MOCK_DB'] = '1'
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(
                standard_args +
                ['export_disdrodlDB2NC.py',
                '-c', 'configs_netcdf/config_008_GV.yml',
                '-d', '2024-01-01',
                '-v', 'bad'],
                capture_output=True,
                check=True,
                env=env
            )
