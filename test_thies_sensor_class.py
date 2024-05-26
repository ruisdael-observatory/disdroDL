"""
Imports
"""
import unittest
from unittest.mock import MagicMock, patch, call
from modules.sensors import Thies, SensorType  # pylint: disable=import-error


class TestThies(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Class for testing the Thies class
    """

    @patch('modules.sensors.serial.Serial')
    @patch('modules.sensors.sys.exit')
    def test_init_serial_connection_exception(self, mock_sys_exit, mock_serial):
        """
        Test if the init_serial_connection function raises
        an exception when the serial connection fails
        :param mock_sys_exit: the mocked exit function
        :param mock_serial: the mocked Serial object
        """
        sensor = Thies()
        logger = MagicMock()
        mock_serial.side_effect = Exception('Serial connection failed')
        sensor.init_serial_connection(port='/dev/ttyACM0', baud=9600, logger=logger)

        logger.error.assert_called_once()
        mock_sys_exit.assert_called_once()

    @patch('modules.sensors.serial.Serial')
    def test_init_serial_connection(self, mock_serial):
        """
        Test if the init_serial_connection function initializes the serial connection correctly
        :param mock_serial: the mocked Serial object
        """
        thies = Thies()
        logger = MagicMock()
        thies.init_serial_connection(port='/dev/ttyACM0', baud=9600, logger=logger)
        mock_serial.assert_called_once_with('/dev/ttyACM0', 9600, timeout=5)

    @patch('modules.sensors.NowTime')
    @patch('modules.sensors.sleep', return_value=None)
    @patch('modules.sensors.serial.Serial')
    def test_sensor_start_sequence(self, mock_serial, mock_sleep, mock_now_time):  # pylint: disable=unused-argument
        """
        Test if the sensor_start_sequence function initializes the thies sensor correctly
        it also tests if all the commands are sent in the correct order
        :param mock_serial: the mocked Serial object
        :param mock_sleep: temporary argument for now
        :param mock_now_time: the mocked NowTime object
        """

        thies = Thies()
        thies.thies_id = '06'
        thies.serial_connection = mock_serial

        logger = MagicMock()

        now_time_instance = MagicMock()
        now_time_instance.time_list = ['10', '20', '30']
        mock_now_time.return_value = now_time_instance

        thies.sensor_start_sequence(config_dict={}, logger=logger)

        logger.info.assert_called_once()
        calls = [
            call.reset_input_buffer(),
            call.reset_output_buffer(),
            call.write('\r06KY00001\r'.encode('utf-8')),
            call.write('\r06TM00000\r'.encode('utf-8')),
            call.write(f'\r06ZH000{now_time_instance.time_list[0]}\r'.encode('utf-8')),
            call.write(f'\r06ZM000{now_time_instance.time_list[1]}\r'.encode('utf-8')),
            call.write(f'\r06ZS000{now_time_instance.time_list[2]}\r'.encode('utf-8')),
            call.write('\r06KY00000\r'.encode('utf-8')),
            call.reset_input_buffer(),
            call.reset_output_buffer()
        ]
        mock_serial.assert_has_calls(calls, any_order=False)

    @patch('modules.sensors.serial.Serial')
    @patch('modules.sensors.sleep', return_value=None)
    def test_reset_sensor(self, mock_sleep, mock_serial):  # pylint: disable=unused-argument
        """
        Test if the reset_sensor function resets the sensor correctly
        :param mock_sleep: temporary argument for now
        :param mock_serial: the mocked Serial object
        """
        thies = Thies()
        thies.thies_id = '06'
        thies.serial_connection = MagicMock()
        logger = MagicMock()
        thies.reset_sensor(logger, True)
        logger_calls = [
            call.info(msg='Resetting Thies'),
            call.info(msg='Thies reset complete')
        ]

        serial_calls = [
            call.write('\r06KY00001\r'.encode('utf-8')),
            call.write('\r06RS00001\r'.encode('utf-8')),
            call.write('\r06RF00001\r'.encode('utf-8')),
            call.write('\r06RA00001\r'.encode('utf-8')),
            call.write('\r06KY00000\r'.encode('utf-8'))
        ]

        logger.assert_has_calls(logger_calls)
        thies.serial_connection.assert_has_calls(serial_calls, any_order=False)

    def test_write_fail(self):
        """
        Test if the logger writes an error when there is an exception in the write function
        """
        thies = Thies()
        logger = MagicMock()
        thies.write("test", logger)
        logger.error.assert_called_once()

    def test_write_successful(self):
        """
        Test if the write function writes the message to the serial connection
        and nothing gets written to the logger
        """
        thies = Thies()
        logger = MagicMock()
        thies.serial_connection = MagicMock()
        thies.write("test", logger)
        thies.serial_connection.write.assert_called_once_with("test")
        logger.assert_not_called()

    def test_read_fail(self):
        """
        Test if the read function writes an error to the logger when there is an exception
        """
        thies = Thies()
        logger = MagicMock()
        return_value = thies.read(logger)
        logger.error.assert_called_once_with(msg="serial_connection not initialized")
        assert return_value is None

    def test_read_successful(self):
        """
        Test if the read function reads the data from the serial connection
        """
        thies = Thies()
        logger = MagicMock()
        mock_serial = MagicMock()
        mock_serial.readline.return_value = "telegram".encode('utf-8')
        thies.serial_connection = mock_serial
        return_value = thies.read(logger)
        thies.serial_connection.readline.assert_called_once()
        logger.error.assert_not_called()
        assert return_value is not None

    def test_get_type(self):
        """
        Test if the get_type function returns the correct sensor type
        """
        thies = Thies()
        assert thies.get_type() == SensorType.THIES
