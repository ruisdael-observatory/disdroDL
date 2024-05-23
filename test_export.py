'''
Module for testing export_disdrodlDB2NC.py
'''

import subprocess
import sys
import unittest
import os
from unittest.mock import patch, MagicMock
from modules.sqldb import query_db_rows_gen, connect_db

env = os.environ.copy()
standard_args = [sys.executable]

# Uncomment the line below to get coverage reports (run 'coverage combine' to combine them with the main report) 
# standard_args = standard_args + ['-m', 'coverage', 'run', '--parallel-mode']

def test_parsivel_full():
    env['MOCK_DB'] = '1'
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_008_GV.yml', '-d', '2024-01-01', '-v', 'full'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 0

def test_parsivel_light():
    env['MOCK_DB'] = '1'
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_008_GV.yml', '-d', '2024-01-01', '-v', 'light'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 0

def test_thies_full():
    env['MOCK_DB'] = '2'
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_008_GV_THIES.yml', '-d', '2024-05-13', '-v', 'full'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 0

def test_thies_light():
    env['MOCK_DB'] = '2'
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_008_GV_THIES.yml', '-d', '2024-05-13', '-v', 'light'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 0

def test_bad_config():
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_000.yml', '-d', '2024-05-13', '-v', 'bad'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 1

def test_bad_date():
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_008_GV.yml', '-d', '2024', '-v', 'full'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 1

def test_bad_version():
    result = subprocess.run(
        standard_args + ['export_disdrodlDB2NC.py', '-c', 'configs_netcdf/config_008_GV.yml', '-d', '2024-05-13', '-v', 'full'], 
        capture_output=True, 
        env=env
    )
    assert result.returncode == 1
