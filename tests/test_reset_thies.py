"""
Test module for reset_sensor.py with Thies sensor
"""
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, call

from reset_sensor import main

wd = Path(__file__).parent.parent


class TestResetThies(unittest.TestCase):
    """
    Class for testing reset_sensor.py with Thies sensor
    """

    @patch('reset_sensor.create_logger')
    @patch('reset_sensor.yaml2dict')
    @patch('reset_sensor.Thies')
    def test_main(self, mock_thies, mock_yaml2dict, mock_create_logger):
        """
        Tests for the main function
        :param mock_thies: Mock object for the Thies call
        :param mock_yaml2dict: Mock object for the yaml2dict call
        :param mock_create_logger: Mock object for the create_logger call
        """
        test_conf_dict = {
            'log_dir': 'value1',
            'script_name': 'value2',
            'global_attrs': {
                'sensor_name': 'thies',
                'sensor_type': 'Thies Clima'
            },
            'port': 'value4',
            'baud': 'value5'
        }

        mock_yaml2dict.return_value = test_conf_dict
        mock_logger = Mock()
        mock_create_logger.return_value = mock_logger

        mock_thies_obj = Mock()
        mock_thies.return_value = mock_thies_obj

        main('config_general_thies.yml')

        expected_calls_yaml2dict = [
            call(path=wd / 'configs_netcdf' / 'config_general_thies.yml')
        ]

        mock_yaml2dict.assert_has_calls(expected_calls_yaml2dict)
        mock_thies.assert_called_once()
        mock_create_logger.assert_called_with(log_dir=Path('value1'),
                                              script_name='value2',
                                              sensor_name='thies')

        (mock_thies_obj.init_serial_connection.
         assert_called_once_with(port=test_conf_dict['port'], baud=test_conf_dict['baud'], logger=mock_logger))
        mock_thies_obj.reset_sensor.assert_called_once_with(logger=mock_logger, factory_reset=False)
