import time
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict
import serial
from  util_functions import yaml2dict
from log import log 

def init_serial(port: str, baud: int):
    try:
        parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
        logger.info(msg='Connected to parsivel {parsivel}')
    except Exception as e:
        logger.error(msg=e)
        print(e)
        sys.exit()
    parsivel.reset_input_buffer()              
    return parsivel


wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

# set up log
log_dir = wd / config_dict['log_dir']
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_file = log_dir / 'log.json'
logger = log(log_path=log_file, 
            log_name=f"{config_dict['script_name']}: {config_dict['Parsivel_name']}")  
logger.info(msg=f"Starting {config_dict['script_name']} for {config_dict['Parsivel_name']}")

# set up data dir
data_dir = wd / config_dict['data_dir']
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
print(data_dir)


# intiated serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'])

while True:
    try:
        parsivel_bytes = parsivel.readline()  # Reads the output the serial communication
        now_utc = datetime.utcnow()
        now_utc_iso = now_utc.isoformat()
        now_utc_ymd = now_utc.strftime("%Y%m%d")
        filename = now_utc_ymd + '.csv'
        filename_field_d61 = now_utc_ymd + '_field61.csv'
        if len(parsivel_bytes) >= 0 and len(parsivel_bytes) <= 5:
            print(parsivel_bytes)

        elif len(parsivel_bytes)> 5 and len(parsivel_bytes) < 20:
            # field 61
                with open(data_dir / filename_field_d61, "a") as g:  # 61
                    writer = csv.writer(g, delimiter=";")
                    # TODO time.time in UTC
                    writer.writerow([now_utc_iso, parsivel_bytes]) 
                    logger.info(msg='Written row to {filename_field_d61}')
                print(parsivel_bytes)

        else: 
            # message with all fields, except 61
            with open(data_dir / filename, "a") as f:
                    writer = csv.writer(f, delimiter=";")

                    parsivel.write(config_dict['parsivel_request_field_61'].encode('utf-8'))  # write to serial

                    writer.writerow([now_utc_iso, parsivel_bytes])
                    print(parsivel_bytes)
                    logger.info(msg='Written row to {filename}')


#               send_data.SendtoWebServer()
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
    time.sleep(1)
