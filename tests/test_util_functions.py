"""
This module contains tests for various functions used in the application.

It includes tests for the logger and the configuration dictionary.
The logger test checks if the log message is correctly written to the log file.
The configuration dictionary test checks the integrity of the configuration dictionary,
ensuring that all expected keys are present.

Functions:
- test_logger: Tests the logger by creating a log message and checking if the message is written to the log file.
- test_config_dict: Tests the integrity of the configuration dictionary `config_dict`.
- test_get_general_config_dict: Tests whether for exporting the correct general config file
    is chosen based on the site config file.
"""
import json
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

from pydantic.v1.utils import deep_update

from modules.sensors import Thies, Parsivel
from modules.util_functions import yaml2dict, get_general_config_dict, create_logger, \
    create_dir, resetSerialBuffers, interruptHandler, create_sensor  # pylint: disable=import-error
from modules.netCDF import unpack_telegram_from_db

wd = Path(__file__).parent.parent
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general_parsivel.yml')
config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_007_CABAUW.yml')
config_dict = deep_update(config_dict, config_dict_site)

telegram_lines = [b'OK\r\n',
                  b'\n',
                  b'SVFS:0000.000;0000.00;00;00;   NP;   C;-9.999;20000;00059;12773;00000;012;450994;2.11.6;2.11.1;0.50;24.3;0;14:09:59;16.02.2023;;;0000.00;000;025;013;013;00.000;0000.0;0000.00;-9.99;0000.00;0000.00;00000007;\n',  # pylint: disable=line-too-long
                  # pylint: disable=line-too-long
                  b'F90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n',
                  # pylint: disable=line-too-long
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


class UtilFunctionsTests(unittest.TestCase):
    """
    Class for testing the functionality of the methods
    """

    @staticmethod
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
        with open(log_file, 'r') as log_file_r:  # pylint: disable=unspecified-encoding
            last_log_line = log_file_r.readlines()[-1]
            last_log_line = json.loads(last_log_line)
            assert last_log_line['name'] == f"{Path(__file__).name}: {config_dict['global_attrs']['sensor_name']}"
            assert last_log_line['msg'] == f"Testing logger in {__file__}"

    @staticmethod
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

    @staticmethod
    def test_get_general_config_dict_parsivel():
        """
        This function tests whether for exporting the correct
         general config file is chosen based on the site config file.
        """
        mock_logger = Mock()

        config_dict_par008 = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV.yml')
        config_dict_general = get_general_config_dict(wd, config_dict_par008['global_attrs']['sensor_type'], mock_logger)

        assert config_dict_general['telegram_fields']['03']['var_attrs']['standard_name'] == 'code_4680'
        mock_logger.error.assert_not_called()

    @staticmethod
    def test_get_general_config_dict_thies():
        """
        This function tests whether for exporting the correct
         general config file is chosen based on the site config file.
        """
        mock_logger = Mock()

        config_dict_thies006 = yaml2dict(path=wd / 'configs_netcdf' / 'config_006_GV_THIES.yml')
        config_dict_general = get_general_config_dict(wd, config_dict_thies006['global_attrs']['sensor_type'], mock_logger)

        assert config_dict_general['telegram_fields']['3']['var_attrs']['standard_name'] == 'serial_number'
        mock_logger.error.assert_not_called()

    @staticmethod
    def test_get_general_config_dict_unsupported_sensor():
        """
        This function tests whether for exporting the correct
         general config file is chosen based on the site config file.
        """
        mock_logger = Mock()

        config_dict_general = get_general_config_dict(wd, 'unsupported_sensor', mock_logger)

        mock_logger.error.assert_called_once()

    @patch('modules.util_functions.os.path.exists', return_value=False)
    @patch('modules.util_functions.Path.mkdir')
    def test_create_dir_1(self, mock_path_mkdir, mock_os_path_exists):
        """
        Test for the create_dir function
        :param mock_path_mkdir: Mock object for the Path.mkdir call
        :param mock_os_path_exists: Mock object for the os.path.exists call
        """
        res = create_dir(wd)

        mock_os_path_exists.assert_called_once_with(wd)
        mock_path_mkdir.assert_called_once_with(wd, parents=True)
        assert res is True

    @patch('modules.util_functions.os.path.exists', return_value=True)
    @patch('modules.util_functions.Path.mkdir')
    def test_create_dir_2(self, mock_path_mkdir, mock_os_path_exists):
        """
        Test for the create_dir function
        :param mock_path_mkdir: Mock object for the Path.mkdir call
        :param mock_os_path_exists: Mock object for the os.path.exists call
        """
        res = create_dir(wd)

        mock_os_path_exists.assert_called_once_with(wd)
        mock_path_mkdir.assert_not_called()
        assert res is False

    @patch('modules.util_functions.sleep')
    def test_reset_serial_buffers(self, mock_sleep):
        """
        Test for the resetSerialBuffers function
        :param mock_sleep: Mock object for the sleep call
        """
        mock_serial_connection = Mock()

        resetSerialBuffers(mock_serial_connection)

        mock_serial_connection.reset_input_buffer.assert_called_once()
        mock_serial_connection.reset_input_buffer.assert_called_once()
        mock_sleep.assert_called_once_with(1)

    @patch('modules.util_functions.print')
    @patch('modules.util_functions.resetSerialBuffers')
    def test_interrupt_handler(self, mock_reset_serial_buffers, mock_print):
        """
        Test for the interruptHandler function
        :param mock_reset_serial_buffers: Mock object for the resetSerialBuffers function call
        :param mock_print: Mock object for the print call
        """
        mock_logger = Mock()
        mock_serial_connection = Mock()

        interruptHandler(mock_serial_connection, mock_logger)

        mock_reset_serial_buffers.assert_called_once_with(serial_connection=mock_serial_connection)
        mock_print.assert_called_once_with('Interrupting execution')
        mock_logger.info.assert_called_with(msg='Interrupting execution')
        mock_serial_connection.close.assert_called_once()

    def test_create_sensor_parsivel(self):
        """
        Test for the create_sensor function with a Parsivel sensor
        """

        mock_logger = Mock()
        sensor_type = 'OTT Hydromet Parsivel2'
        sensor = create_sensor(sensor_type=sensor_type, logger=mock_logger, sensor_id='00')
        assert isinstance(sensor, Parsivel)
        mock_logger.assert_not_called()

    def test_create_sensor_thies(self):
        """
        Test for the create_sensor function with a Thies sensor
        """

        mock_logger = Mock()
        sensor_type = 'Thies Clima'
        sensor_id = '06'
        sensor = create_sensor(sensor_type=sensor_type, logger=mock_logger, sensor_id=sensor_id)
        assert isinstance(sensor, Thies)
        assert sensor.thies_id == sensor_id
        mock_logger.assert_not_called()

    @patch('modules.util_functions.sys')
    def test_create_sensor_fail(self, mock_sys):
        """
        Test for the create_sensor function with a non-supported sensor type
        """

        mock_logger = Mock()
        sensor_type = 'fail'
        sensor_id = '06'
        sensor = create_sensor(sensor_type=sensor_type, logger=mock_logger, sensor_id=sensor_id)
        mock_logger.error.called_once_with(msg="Sensor type fail not recognized")
        mock_sys.exit.called_once_with(1)

    @staticmethod
    def test_unpack_telegram_from_db_no_None():
        """
        Test for the unpack_telegram_from_db function with no None values
        """
        input_str = "20:10; 21:25.05.2023; 51:000140; 90:-9.999,-9.999,-9.999,-9.999"
        expected_output = {
            '20': '10',
            '21': '25.05.2023',
            '51': '000140',
            '90': '-9.999,-9.999,-9.999,-9.999'
        }
        assert unpack_telegram_from_db(input_str) == expected_output

    @staticmethod
    def test_unpack_telegram_from_db_with_None():
        """
        Test for the unpack_telegram_from_db function with a None value
        """
        input_str = "19:None; 20:10; 21:25.05.2023; 51:000140; 90:-9.999,-9.999,-9.999,-9.999"
        expected_output = {
            '19': None,
            '20': '10',
            '21': '25.05.2023',
            '51': '000140',
            '90': '-9.999,-9.999,-9.999,-9.999'
        }
        assert unpack_telegram_from_db(input_str) == expected_output
