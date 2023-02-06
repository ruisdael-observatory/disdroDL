import re
import serial
import sys
from time import sleep
from pathlib import Path
from  util_functions import yaml2dict
from parsivel_cmds import *
from  util_functions import yaml2dict, create_dir, create_new_csv, binary2list, init_serial


print(__file__)
wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

def init_serial(port: str, baud: int):
    try:
        parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
    except Exception as e:
        print(e)
        sys.exit()
    parsivel.reset_input_buffer()              
    return parsivel



parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'])
parsivel.reset_input_buffer()  # Flushes input buffer
parsivel.write(parsivel_pooling_mood)  
parsivel.write('CS/M/M/0\r'.encode('utf-8')) # 1=user telegram ; 0= ott telegram
parsivel.write('CS/M/S/F03:%03;F04:%04;F05:%05;F06:%06\r'.encode('utf-8'))
#parsivel.write('CS/M/S/%60'.encode('utf-8'))
# parsivel.write(parsivel_set_telegram_list) # Writes the parsivel user telegram string to the Parsivel

sleep(float(.5))
#parsivel.write('CS/R\r'.encode('utf-8')) # repeate poll
telegram=parsivel.readline()
print('telegram:', telegram)
parsivel.close()
