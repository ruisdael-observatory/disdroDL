import serial
from time import sleep


parsivel = serial.Serial( '/dev/ttyUSB0', 19200, timeout=1)  # Defines the serial port
parsivel.reset_input_buffer()  # Flushes input buffer

parsivel.write('CS/P\r\n'.encode('utf-8'))  # needed:yes
sleep(1) # needed?

user_telegram_str = (f'CS/M/S/%93;\r').encode('utf-8')
parsivel.write(user_telegram_str)  # string format
parsivel_lines = parsivel.readlines()
print(parsivel_lines)
