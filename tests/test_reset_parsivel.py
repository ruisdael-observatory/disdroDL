"""
Module for testing reset_sensor.py with Parsivel sensor
"""
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, call

import reset_sensor
from reset_sensor import get_config_file

wd = Path(__file__).parent.parent


class TestResetParsivel(unittest.TestCase):
    """
    Class for testing reset_sensor.py with Parsivel
    """

    @patch('reset_sensor.ArgumentParser')
    def test_get_config_file(self, mock_argument_parser):
        """
        Tests for the get_config_file function
        :param mock_argument_parser: Mock object for the ArgumentParser call
        """
        mock_parser = Mock()
        mock_argument_parser.return_value = mock_parser
        mock_args = Mock()
        mock_args.config = "config_008_GV.yml"
        mock_parser.parse_args.return_value = mock_args

        res = get_config_file()

        self.assertEqual(res, "config_008_GV.yml")
        mock_argument_parser.assert_called_once_with(
            description="Ruisdael: OTT Disdrometer reset. Run: python reset_sensor.py -c config_*.yml"
        )
        mock_parser.add_argument.assert_called_once_with('-c',
                                                         '--config',
                                                         required=True,
                                                         help='Observation site config file. ie. -c config_008_GV.yml')
        mock_parser.parse_args.assert_called_once()

    @patch('reset_sensor.create_logger')
    @patch('reset_sensor.yaml2dict')
    @patch('reset_sensor.Parsivel')
    def test_main(self, mock_parsivel, mock_yaml2dict, mock_create_logger):
        """
        Tests for the main function
        :param mock_parsivel: Mock object for the Parsivel call
        :param mock_yaml2dict: Mock object for the yaml2dict call
        :param mock_create_logger: Mock object for the create_logger call
        """
        test_conf_dict = {
            'log_dir': 'value1',
            'script_name': 'value2',
            'global_attrs': {
                'sensor_name': 'parsivel',
                'sensor_type': 'OTT Hydromet Parsivel2'
            },
            'port': 'value4',
            'baud': 'value5'
        }

        mock_yaml2dict.return_value = test_conf_dict

        mock_logger = Mock()
        mock_create_logger.return_value = mock_logger

        mock_parsivel_obj = Mock()
        mock_parsivel.return_value = mock_parsivel_obj

        expected_calls_yaml2dict = [
            call(path=wd / 'configs_netcdf' / 'config_008_GV.yml')
        ]

        reset_sensor.main('config_008_GV.yml')

        mock_yaml2dict.assert_has_calls(expected_calls_yaml2dict)
        mock_parsivel.assert_called_once()
        mock_create_logger.assert_called_with(log_dir=Path('value1'),
                                                   script_name='value2',
                                                   sensor_name='parsivel')
        (mock_parsivel_obj.init_serial_connection.
         assert_called_once_with(port=test_conf_dict['port'], baud=test_conf_dict['baud'], logger=mock_logger))
        mock_parsivel_obj.reset_sensor.assert_called_once()
