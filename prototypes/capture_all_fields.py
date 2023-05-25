import serial
from time import sleep
import chardet
from datetime import datetime

parsivel = serial.Serial( '/dev/ttyUSB0', 19200, timeout=1)  # Defines the serial port
parsivel.reset_input_buffer()  # Flushes input buffer

sleep(2)
while True:
    print(datetime.now().isoformat())
    parsivel.write('CS/PA\r\n'.encode('ascii'))
    parsivel_lines = parsivel.readlines()
    for i in parsivel_lines:
        encoding = chardet.detect(i)['encoding']
        # print(i) 
        # print(encoding)
        i_str = i.decode(encoding)
        i_list = i_str.split(":")
        if len(i_list) > 1 and i_list[1].strip() != ";":
            field = i_list[0]
            value = i_list[1].strip() # strip white space
            print(f'value: "{value}"')
            value_list = value.split(";")
            value_list = [v for v in value_list if len(v) > 0]
            print(f'F:{field} value_list: {value_list}')
            if field == '93':
                print(len(value_list))
                assert len(value_list) == 1024  # test
    sleep(60)