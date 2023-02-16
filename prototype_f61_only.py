import csv
import re
from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict, create_dir, create_new_csv, init_serial, parsivel_list_2_csv
from parsivel_cmds import *
from log import log 
from time import sleep


print('starting script')

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

# intiated serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
parsivel.reset_input_buffer()  # Flushes input buffer
parsivel.write('CS/Z/1\r\n'.encode('utf-8'))  # Restart sensor, reset the rain amount
sleep(10)
parsivel.write('CS/M/M/1\r\n'.encode('utf-8')) # User defined telegram

svfs_cmd = 'CS/M/S/F61:%61;\r\n'
parsivel.write(svfs_cmd)
sleep(1)
parsivel.write('CS/P\r\n'.encode('utf-8'))
telegram_lines=parsivel.readlines()
print(telegram_lines)

for telegram_line in telegram_lines:
    print('line', telegram_line)

