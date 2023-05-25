import serial
from time import sleep

encoding = 'Windows-1252'  # 'utf-8'

parsivel = serial.Serial( '/dev/ttyUSB0', 19200, timeout=1)  # Defines the serial port
parsivel.reset_input_buffer()  # Flushes input buffer

sleep(2)
parsivel.write('CS/P\r\n'.encode(encoding))  # needed:yes
sleep(5) # needed?

user_telegram_str = (f'CS/M/S/%93;\r').encode(encoding)
parsivel.write(user_telegram_str)  # string format
parsivel_lines = parsivel.readlines()
print(parsivel_lines)

f_93_str = parsivel_lines[0].decode(encoding='Windows-1252', errors='strict')
print(f_93_str)
f_93_list = f_93_str.split(';')
print('len F93:', len(f_93_list))
