import time
from unittest import mock

from modules.now_time import NowTime
from modules.sensors import Thies, SensorType


@mock.patch('serial.Serial')
@mock.patch('sys.exit')
def test_init_serial_connection_exception(mock_sys_exit, mock_serial):
    sensor = Thies()
    logger = mock.MagicMock()

    mock_serial.side_effect = Exception('Serial connection failed')
    sensor.init_serial_connection(port='/dev/ttyACM0', baud=9600, logger=logger)

    logger.error.assert_called_once()
    mock_sys_exit.assert_called_once()


@mock.patch('serial.Serial')
def test_init_serial_connection(mock_serial):
    thies = Thies()
    logger = mock.MagicMock()
    thies.init_serial_connection(port='/dev/ttyACM0', baud=9600, logger=logger)
    mock_serial.assert_called_once_with('/dev/ttyACM0', 9600, timeout=1)


@mock.patch('time.sleep', return_value=None)
@mock.patch('serial.Serial')
def test_sensor_start_sequence(mock_serial, mock_sleep):


    thies = Thies()
    thies.thies_id = '06'
    thies.serial_connection = mock_serial

    logger = mock.MagicMock()
    mock_sleep.return_value = None
    with mock.patch('modules.now_time.NowTime.time_list', ['10', '20', '30']):
        thies.sensor_start_sequence(config_dict={}, logger=logger)

    logger.info.assert_called_once()
    calls = [
        mock.call.reset_input_buffer(),
        mock.call.reset_output_buffer(),
        mock.call.write('\r06KY00001\r'.encode('utf-8')),
        mock.call.write('\r06TM00000\r'.encode('utf-8')),
        mock.call.write(f'\r06ZH000{10}\r'.encode('utf-8')),
        mock.call.write(f'\r06ZM000{20}\r'.encode('utf-8')),
        mock.call.write(f'\r06ZS000{30}\r'.encode('utf-8')),
        mock.call.write('\r06KY00000\r'.encode('utf-8')),
        mock.call.reset_input_buffer(),
        mock.call.reset_output_buffer()
    ]
    mock_serial.assert_has_calls(calls, any_order=False)


def test_write_fail():
    thies = Thies()
    logger = mock.MagicMock()
    thies.write("test", logger)
    logger.error.assert_called_once()


def test_write_successful():
    thies = Thies()
    logger = mock.MagicMock()
    thies.serial_connection = mock.MagicMock()
    thies.write("test", logger)
    thies.serial_connection.write.assert_called_once_with("test")
    logger.assert_not_called()


def test_read_fail():
    thies = Thies()
    logger = mock.MagicMock()
    return_value = thies.read(logger)
    logger.error.assert_called_once_with(msg="serial_connection not initialized")
    assert return_value is None


def test_read_successful():
    thies = Thies()
    logger = mock.MagicMock()
    mock_serial = mock.MagicMock()
    mock_serial.readline.return_value = "telegram"
    thies.serial_connection = mock_serial
    return_value = thies.read(logger)
    thies.serial_connection.readline.assert_called_once()
    logger.error.assert_not_called()
    assert return_value is not None


def test_get_type():
    thies = Thies()
    assert thies.get_type() == SensorType.THIES


def test_get_serial_connection():
    thies = Thies()
    assert thies.get_serial_connection() is None


def test_get_serial_connection2():
    thies = Thies()
    mock_serial = mock.MagicMock()
    thies.serial_connection = mock_serial
    assert thies.get_serial_connection() == mock_serial
