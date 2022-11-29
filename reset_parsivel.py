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

# parsivel.write(parsivel_ott_telegram) # Writes the Parsivel OTT telegram command to the Parsivel
sleep(1)
parsivel.write(parsivel_user_telegram)
sleep(1)
parsivel.write(parsivel_set_telegram_list) # Writes the parsivel user telegram string to the Parsivel
sleep(1)
parsivel.write(parsivel_telegram_command)
sleep(1)
parsivel.write(parsivel_command_list)
sleep(1)
parsivel.write(parsivel_telegram_start)
sleep(1)
parsivel.write(parsivel_current_configuration)
sleep(1)
parsivel.write(parsivel_impulse_mode)
sleep(1)
parsivel.write(parsivel_set_station_name)
sleep(1)
parsivel.write(parsivel_set_ID)
sleep(1)
parsivel.write(parsivel_real_time)
sleep(1)
parsivel.write(parsivel_set_time)
sleep(1)
parsivel.write(parsivel_request_field_90)
sleep(1)
parsivel.write(parsivel_set_real_time)
sleep(1)
parsivel.write(parsivel_restart)
sleep(1)
parsivel.write('CS/R/19\r'.encode('utf-8')) # date and time start

sleep(2)
parsivel.write(parsivel_current_configuration) # ask parsivel for config
for config_line in parsivel.readlines(): # print config
    print(config_line)
