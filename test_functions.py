"""
This module contains tests for various functions used in the application.

It includes tests for the logger and the configuration dictionary.
The logger test checks if the log message is correctly written to the log file.
The configuration dictionary test checks the integrity of the configuration dictionary,
ensuring that all expected keys are present.

Functions:
- test_logger: Tests the logger by creating a log message and checking if the message is written to the log file.
- test_config_dict: Tests the integrity of the configuration dictionary `config_dict`.
"""
import json
from pathlib import Path
import unittest
from pydantic.v1.utils import deep_update
from modules.util_functions import yaml2dict, get_general_config, create_logger # pylint: disable=import-error

wd = Path(__file__).parent
config_dict = yaml2dict(path = wd / 'configs_netcdf' / 'config_general_parsivel.yml')
config_dict_site = yaml2dict(path = wd / 'configs_netcdf' / 'config_007_CABAUW.yml')
config_dict = deep_update(config_dict, config_dict_site)

telegram_lines=[b'OK\r\n',
                b'\n',
                b'SVFS:0000.000;0000.00;00;00;   NP;   C;-9.999;20000;00059;12773;00000;012;450994;2.11.6;2.11.1;0.50;24.3;0;14:09:59;16.02.2023;;;0000.00;000;025;013;013;00.000;0000.0;0000.00;-9.99;0000.00;0000.00;00000007;\n', # pylint: disable=line-too-long
                b'F90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n', # pylint: disable=line-too-long
                b'F91:00.000;00.000;00.000;00.000;00.000;\n',
                b'F93:000;000;000;000;000;000;\n',
                b'F61:00.502;00.853\r\n',
                b'00.606;02.026\r\n',
                b'00.550;01.595\r\n',
                b'00.521;01.237\r\n',
                b'00.540;01.070\r\n',
                b'00.559;01.710\r\n',
                b'00.571;01.572\r\n',
                b';']


def test_logger():
    """
    This function tests the logger by creating a log message and checking if the message is written to the log file.
    """
    logger = create_logger(
        log_dir=Path(config_dict['log_dir']),
        script_name=Path(__file__).name,
        sensor_name=config_dict['global_attrs']['sensor_name']
    )
    logger.info(msg=f"Testing logger in {__file__}")
    assert logger.name == f"{Path(__file__).name}: {config_dict['global_attrs']['sensor_name']}"
    log_file = Path(config_dict['log_dir']) / f'log_{Path(__file__).name}.json'
    with open(log_file, 'r') as log_file_r: # pylint: disable=unspecified-encoding
        last_log_line = log_file_r.readlines()[-1]
        last_log_line = json.loads(last_log_line)
        assert last_log_line['name'] == f"{Path(__file__).name}: {config_dict['global_attrs']['sensor_name']}"
        assert last_log_line['msg'] == f"Testing logger in {__file__}"


def test_config_dict():
    """
    This function tests the integrity of the configuration dictionary `config_dict`.
    It checks if the expected keys are present in the dictionary and also if
    the expected keys are present in the 'variables' sub-dictionary.
    If any of the keys are not found, an AssertionError will be raised.
    """
    for key in ['dimensions', 'variables', 'telegram_fields',
                'station_code', 'port', 'baud', 'script_name', 'data_dir',
                'log_dir', 'global_attrs', 'variables']:
        assert key in config_dict.keys()
    for variable_key in ['time', 'interval', 'datetime', 'latitude', 'longitude', 'altitude']:
        assert variable_key in config_dict['variables'].keys()

#  'velocity_classes_center', 'velocity_upper_bounds', 'velocity_lower_bounds', 'velocity_spread',

def test_get_general_config():
    """
    This function tests whether for exporting the correct general config file is chosen based on the site config file.
    """
    config_dict_par008 = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV.yml')
    config_dict_general = get_general_config(wd, config_dict_par008['global_attrs']['sensor_type'])
    assert config_dict_general['telegram_fields']['03']['var_attrs']['standard_name'] == 'code_4680'

    config_dict_thies006 = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV_THIES.yml')
    config_dict_general = get_general_config(wd, config_dict_thies006['global_attrs']['sensor_type'])
    assert config_dict_general['telegram_fields']['3']['var_attrs']['standard_name'] == 'serial_number'

class ExceptionTests(unittest.TestCase):
    """
    Class to make testing exceptions possible
    """

    def test_unsupported_site_config(self):
        """
        This function varifies that a site config file with an unsupported sensor type will cause an error to be thrown.
        """
        with self.assertRaises(Exception):
            get_general_config(wd, 'unsupported_sensor_type')
