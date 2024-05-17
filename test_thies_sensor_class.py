"""
Imports
"""
from unittest import mock
from modules.sensors import Thies, SensorType # pylint: disable=import-error


@mock.patch('modules.sensors.serial.Serial')
@mock.patch('modules.sensors.sys.exit')
def test_init_serial_connection_exception(mock_sys_exit, mock_serial):
    """
    Test if the init_serial_connection function raises
    an exception when the serial connection fails
    :param mock_sys_exit: the mocked exit function
    :param mock_serial: the mocked Serial object
    """
    sensor = Thies()
    logger = mock.MagicMock()

    mock_serial.side_effect = Exception('Serial connection failed')
    sensor.init_serial_connection(port='/dev/ttyACM0', baud=9600, logger=logger)

    logger.error.assert_called_once()
    mock_sys_exit.assert_called_once()


@mock.patch('modules.sensors.serial.Serial')
def test_init_serial_connection(mock_serial):
    """
    Test if the init_serial_connection function initializes the serial connection correctly
    :param mock_serial: the mocked Serial object
    """
    thies = Thies()
    logger = mock.MagicMock()
    thies.init_serial_connection(port='/dev/ttyACM0', baud=9600, logger=logger)
    mock_serial.assert_called_once_with('/dev/ttyACM0', 9600, timeout=1)


@mock.patch('modules.sensors.NowTime')
@mock.patch('modules.sensors.sleep', return_value=None)
@mock.patch('modules.sensors.serial.Serial')
def test_sensor_start_sequence(mock_serial, mock_sleep, mock_now_time): # pylint: disable=unused-argument
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

    logger = mock.MagicMock()

    now_time_instance = mock.MagicMock()
    now_time_instance.time_list = ['10', '20', '30']
    mock_now_time.return_value = now_time_instance

    thies.sensor_start_sequence(config_dict={}, logger=logger)

    logger.info.assert_called_once()
    calls = [
        mock.call.reset_input_buffer(),
        mock.call.reset_output_buffer(),
        mock.call.write('\r06KY00001\r'.encode('utf-8')),
        mock.call.write('\r06TM00000\r'.encode('utf-8')),
        mock.call.write(f'\r06ZH000{now_time_instance.time_list[0]}\r'.encode('utf-8')),
        mock.call.write(f'\r06ZM000{now_time_instance.time_list[1]}\r'.encode('utf-8')),
        mock.call.write(f'\r06ZS000{now_time_instance.time_list[2]}\r'.encode('utf-8')),
        mock.call.write('\r06KY00000\r'.encode('utf-8')),
        mock.call.reset_input_buffer(),
        mock.call.reset_output_buffer()
    ]
    mock_serial.assert_has_calls(calls, any_order=False)


def test_write_fail():
    """
    Test if the logger writes an error when there is an exception in the write function
    """
    thies = Thies()
    logger = mock.MagicMock()
    thies.write("test", logger)
    logger.error.assert_called_once()


def test_write_successful():
    """
    Test if the write function writes the message to the serial connection
    and nothing gets written to the logger
    """
    thies = Thies()
    logger = mock.MagicMock()
    thies.serial_connection = mock.MagicMock()
    thies.write("test", logger)
    thies.serial_connection.write.assert_called_once_with("test")
    logger.assert_not_called()


def test_read_fail():
    """
    Test if the read function writes an error to the logger when there is an exception
    """
    thies = Thies()
    logger = mock.MagicMock()
    return_value = thies.read(logger)
    logger.error.assert_called_once_with(msg="serial_connection not initialized")
    assert return_value is None


def test_read_successful():
    """
    Test if the read function reads the data from the serial connection
    """
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
    """
    Test if the get_type function returns the correct sensor type
    """
    thies = Thies()
    assert thies.get_type() == SensorType.THIES
