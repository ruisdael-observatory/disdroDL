import serial
from time import sleep
import chardet

parsivel = serial.Serial( '/dev/ttyUSB0', 19200, timeout=1)  # Defines the serial port
parsivel.reset_input_buffer()  # Flushes input buffer

sleep(2)
parsivel.write('CS/PA\r\n'.encode('ascii'))

parsivel_lines = parsivel.readlines()
print(parsivel_lines)


# for line in parsivel_lines:
#     encoding = chardet.detect(line)['encoding']
#     line_str = line.decode(encoding)
#     print(line_str, type(line_str))
#     i_list = line_str.split(":")
#     if len(i_list) > 1:
#         field = i_list[0]
#         value = i_list[1]
#         if field == '93':
#             print(field, 'value:', value)
#             value_list = value.split(';')
#             print(len(value_list))

#     else: 
#         print('NO VALUE')

# f_93_str = parsivel_lines[0].decode(encoding='Windows-1252', errors='strict')
# print(f_93_str)
# f_93_list = f_93_str.split(';')
# print('len F93:', len(f_93_list))
