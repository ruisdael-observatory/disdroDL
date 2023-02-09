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


def handle_telegram(telegram_lines):
    '''
    telegram lines comes as list; 
    the 1st item is the telegram and the second one is field 61
    If 

    '''
    

parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'])
parsivel.reset_input_buffer()  # Flushes input buffer

parsivel.write('CS/Z/1\r\n'.encode('utf-8'))  # Restart sensor, reset the rain amount
sleep(10)
parsivel.write('CS/M/M/1\r\n'.encode('utf-8')) # User defined telegram

while True:
    parsivel.write('CS/M/S/%01,%02,%03,%04,%05,%06,%07,%08,%09,%10,%11,%12,%13,%14,%15,%16,%17,%18,%20,%21,%22,%23,%24,%25,%26,%27,%28,%30,%31,%32,%33,%34,%35,%60,\r\n'.encode('utf-8'))
    sleep(1)
    parsivel.write('CS/P\r\n'.encode('utf-8'))
    sleep(1)
    telegram_single_values=parsivel.readline()
    print('telegram:', telegram_single_values)
    sleep(60)

