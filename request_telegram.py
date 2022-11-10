import sys
import serial
from time import sleep
from pathlib import Path
from  util_functions import yaml2dict
from parsivel_cmds import *

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

# setup parsivel config commands 
parsivel.write(parsivel_user_telegram) # set up parsivel: to send user defined telegram 
sleep(2) 
parsivel.write(parsivel_set_telegram_list)  # set up parsivel: defining list of fields 
sleep(2)
parsivel.write(parsivel_current_configuration) # ask parsivel for config
for config_line in parsivel.readlines(): # print config
    print(config_line)