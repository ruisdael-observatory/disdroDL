from unittest import mock
from modules.sensors import Thies

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


# @mock.patch('time.sleep', return_value=None)
# @mock.patch('serial.Serial')
# @mock.patch('modules.now_time.NowTime', 'time_list', [10, 20, 30])
# def test_sensor_start_sequence(mock_serial, mock_sleep):
#     mock_sleep.return_value = None
#     thies = Thies()
#     thies.thies_id = '06'
#     thies.serial_connection = mock_serial
#     mock_now_time = mock.MagicMock()
#     mock_now_time.time_list = [10, 20, 30]
#     logger = mock.MagicMock()
#     thies.sensor_start_sequence(config_dict={}, logger=logger)
#
#     logger.info.assert_called_once()
#     calls = [
#         mock.call.reset_input_buffer(),
#         mock.call.reset_output_buffer(),
#         mock.call.write('06KY00001\r'.encode('utf-8')),
#         mock.call.write('06TM00000\r'.encode('utf-8')),
#         mock.call.write(f'06ZH000{mock_now_time.time_list[0]}\r'.encode('utf-8')),
#         mock.call.write(f'06ZM000{mock_now_time.time_list[1]}\r'.encode('utf-8')),
#         mock.call.write(f'06ZS000{mock_now_time.time_list[2]}\r'.encode('utf-8')),
#         mock.call.write('06KY00000\r'.encode('utf-8')),
#         mock.call.reset_input_buffer(),
#         mock.call.reset_output_buffer()
#     ]
#     mock_serial.assert_has_calls(calls, any_order=False)

