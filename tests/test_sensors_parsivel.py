"""
Module for testing the Parsivel class from sensors.py
"""

import unittest
from unittest.mock import Mock, patch, call
from modules.sensors import Parsivel


class TestParsivel(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Class for testing the Parsivel Sensor subclass.

    Functions:
    - test___init__: Constructor test.
    - test_init_serial_connection_success: Good weather test for the init_serial_connection_success function.
    - test_init_serial_connection_exception: Bad weather test for the init_serial_connection_success function.
    - test_sensor_start_sequence: Test for the sensor_start_sequence function with logging.
    - test_sensor_start_sequence_no_log: Test for the sensor_start_sequence function without logging.
    - test_reset_sensor_factory_reset: Good weather test for the reset_sensor function with factory_reset=True.
    - test_reset_sensor_restart: Good weather test for the reset_sensor function with factory_reset=False.
    - test_write_success: Good weather test for the write function.
    - test_write_fail: Bad weather test for the write function.
    - test_read_success: Good weather test for the read function.
    - test_read_fail: Bad weather test for the read function.
    - test_get_type: Test if the get_type function returns the correct sensor type.
    """

    def test___init__(self):
        """
        Constructor test.
        """
        parsivel = Parsivel()
        assert parsivel.serial_connection is None
        assert parsivel.get_type() == "parsivel"

    @patch('modules.sensors.serial.Serial')
    def test_init_serial_connection_success(self, mock_serial):
        """
        Good weather test for the init_serial_connection_success function.
        :param mock_serial: Mock of the serial.Serial call
        """
        mock_logger = Mock()
        parsivel_obj = Parsivel()

        parsivel_obj.init_serial_connection(port="test", baud=1, logger=mock_logger)

        mock_logger.info.assert_called_once()
        mock_serial.assert_called_once_with("test", 1, timeout=1)

        assert parsivel_obj.serial_connection is not None

    @patch('modules.sensors.serial.Serial', side_effect=Exception('Test'))
    @patch('modules.sensors.sys.exit', side_effect=Exception('Exit'))
    def test_init_serial_connection_exception(self, mock_serial, mock_exit):
        """
        Bad weather test for the init_serial_connection_success function
        :param mock_serial: Mock of the serial.Serial call
                            with an Exception side effect
        :param mock_exit: Mock of the sys.exit call with
                            an Exception side effect, used
                            to prevent the execution of the
                            last line of the function under test
        """
        mock_logger = Mock()
        parsivel_obj = Parsivel()
        try:
            parsivel_obj.init_serial_connection(port="test", baud=1, logger=mock_logger)
        except Exception:  # pylint: disable=broad-except
            mock_serial.assert_called_once()
            mock_logger.error.assert_called_once()
            mock_exit.assert_called_once()

    @patch('modules.sensors.sleep', return_value=None)
    def test_sensor_start_sequence(self, mock_sleep):
        """
        Test for the sensor_start_sequence function with logging.
        :param mock_sleep: Mock of the time.sleep call
        """
        mock_logger = Mock()
        mock_serial_connection = Mock()
        parsivel_obj = Parsivel()
        parsivel_obj.serial_connection = mock_serial_connection
        parsivel_obj.write = Mock()

        config_dict = {
            'station_code': 'STATION1',
            'global_attrs': {
                'sensor_name': '1234'
            }
        }

        expected_calls_write = [
            call(b'CS/K/STATION1\r', mock_logger),
            call(b'CS/J/1234\r', mock_logger),
            call(b'CS/Z/1\r', mock_logger),
            call(b'CS/M/M/1\r', mock_logger)
        ]

        parsivel_obj.sensor_start_sequence(config_dict, mock_logger, True)

        mock_logger.info.assert_called_once_with(msg="Starting parsivel start sequence commands")
        assert mock_serial_connection.reset_input_buffer.call_count == 2

        parsivel_obj.write.assert_has_calls(expected_calls_write)

        expected_calls_sleep = [
            call(1),
            call(2),
            call(10)
        ]

        mock_sleep.assert_has_calls(expected_calls_sleep)

    @patch('modules.sensors.sleep', return_value=None)
    def test_sensor_start_sequence_no_log(self, mock_sleep):
        """
        Test for the sensor_start_sequence function without logging.
        :param mock_sleep: Mock of the time.sleep call
        """
        mock_logger = Mock()
        mock_serial_connection = Mock()
        parsivel_obj = Parsivel()
        parsivel_obj.serial_connection = mock_serial_connection
        parsivel_obj.write = Mock()

        config_dict = {
            'station_code': 'STATION1',
            'global_attrs': {
                'sensor_name': '1234'
            }
        }

        parsivel_obj.sensor_start_sequence(config_dict=config_dict, logger=mock_logger, include_in_log=False)

        mock_logger.info.assert_not_called()

    @patch('modules.sensors.sleep', return_value=None)
    def test_reset_sensor_factory_reset(self, mock_sleep):
        """
        Good weather test for the reset_sensor function with factory_reset=True.
        :param mock_sleep: Mock of the time.sleep call
        """
        mock_serial_connection = Mock()
        parsivel_obj = Parsivel()
        parsivel_obj.serial_connection = mock_serial_connection
        parsivel_obj.write = Mock()
        mock_logger = Mock()

        parsivel_obj.reset_sensor(mock_logger, True)

        mock_logger.info.assert_called_once_with(msg="Resetting Parsivel")
        parsivel_obj.write.assert_called_once_with(b'CS/F/1\r', mock_logger)
        mock_sleep.assert_called_once_with(5)

    @patch('modules.sensors.sleep', return_value=None)
    def test_reset_sensor_restart(self, mock_sleep):
        """
        Good weather test for the reset_sensor function with factory_reset=False.
        :param mock_sleep: Mock of the time.sleep call
        """
        mock_serial_connection = Mock()
        parsivel_obj = Parsivel()
        parsivel_obj.serial_connection = mock_serial_connection
        parsivel_obj.write = Mock()
        mock_logger = Mock()

        parsivel_obj.reset_sensor(mock_logger, False)

        mock_logger.info.assert_called_once_with(msg="Resetting Parsivel")
        parsivel_obj.write.assert_called_once_with(b'CS/Z/1\r', mock_logger)
        mock_sleep.assert_called_once_with(5)

    def test_write_success(self):
        """
        Good weather test for the write function.
        """
        mock_serial_connection = Mock()
        parsivel_obj = Parsivel()
        parsivel_obj.serial_connection = mock_serial_connection
        mock_logger = Mock()

        res = parsivel_obj.write("test", mock_logger)

        assert res is None
        mock_serial_connection.write.assert_called_once_with("test")
        mock_logger.error.assert_not_called()

    def test_write_fail(self):
        """
        Bad weather test for the write function.
        """
        parsivel_obj = Parsivel()
        mock_logger = Mock()

        res = parsivel_obj.write("test", mock_logger)

        assert res is None
        mock_logger.error.assert_called_once_with(msg="serial_connection not initialized")

    def test_read_success(self):
        """
        Good weather test for the read function.
        """
        parsivel_obj = Parsivel()
        mock_serial_connection = Mock()
        mock_serial_connection.readlines.return_value = "test"
        mock_logger = Mock()
        parsivel_obj.serial_connection = mock_serial_connection

        res = parsivel_obj.read(mock_logger)

        assert res == "test"
        mock_logger.error.assert_not_called()

    def test_read_fail(self):
        """
        Bad weather test for the read function.
        """
        parsivel_obj = Parsivel()
        mock_logger = Mock()

        res = parsivel_obj.read(mock_logger)

        assert res is None
        mock_logger.error.assert_called_once_with(msg="serial_connection not initialized")

    def test_get_type(self):
        """
        Test if the get_type function returns the correct sensor type.
        """
        parsivel_obj = Parsivel()

        assert parsivel_obj.get_type() == "parsivel"

    def test_close_serial_connection(self):
        """
        Test for the close_serial_connection function
        """
        parsivel_obj = Parsivel()
        mock_serial_connection = Mock()
        parsivel_obj.serial_connection = mock_serial_connection

        parsivel_obj.close_serial_connection()

        mock_serial_connection.close.assert_called_once()
