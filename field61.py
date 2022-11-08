import time
import csv
import yaml

from datetime import datetime
from pathlib import Path
from typing import Dict
import serial

wd = Path(__file__).parent 


def yaml2dict(path: str) -> Dict:
    with open(path, 'r') as yaml_f:
        yaml_content = yaml_f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    return yaml_dict

def init_serial(port: str, baud: int):
    parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
    parsivel.reset_input_buffer()              
    return parsivel

config_dict = yaml2dict(path = wd / 'config.yml')
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'])
print(parsivel)

parsivel.write('CS/R/61\r'.encode('utf-8'))

while True:
    try:
        parsivel.write('CS/R/61\r'.encode('utf-8'))

        parsivel_bytes = parsivel.readline()  # Reads the output the serial communication
        print(parsivel_bytes, 'byte len:', len(parsivel_bytes))
        # now_utc = datetime.utcnow()
        # now_utc_ymdHMS = now_utc.strftime("%Y%m%d-%H%M%S")
        # now_utc_ymd = now_utc.strftime("%Y%m%d")
        # filename = now_utc_ymd + '.csv'
        # filename_field_d61 = now_utc_ymd + '_field61.csv'
        # if len(parsivel_bytes) >= 0 and len(parsivel_bytes) <= 5:
        #     print(parsivel_bytes)
        # elif len(parsivel_bytes)> 5 and len(parsivel_bytes) < 20:
        #         with open(filename_field_d61, "a") as g:
        #             writer = csv.writer(g, delimiter=";")
        #             # TODO time.time in UTC
        #             writer.writerow([now_utc_ymdHMS, time.time(), parsivel_bytes]) 
        #         print(parsivel_bytes)
        # else:
        #     with open(filename, "a") as f:
        #             writer = csv.writer(f, delimiter=";")
        #             # TODO time.time in UTC
        #             writer.writerow([now_utc_ymdHMS, time.time(), parsivel_bytes])
        #             print(parsivel_bytes)

#               send_data.SendtoWebServer()
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
    time.sleep(60)

# output: b'00.950;03.367\r\n' byte len: 15
# b'00.564;02.451\r\n' byte len: 15
# b'00.865;03.704\r\n' byte len: 15
# b'00.841;03.529\r\n' byte len: 15
# b'00.947;03.325\r\n' byte len: 15