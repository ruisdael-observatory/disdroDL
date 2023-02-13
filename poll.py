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

flag_zero_seconds = False
while True:
    now_min_secs = datetime.utcnow().strftime("%M:%S")
    now_min_secs = now_min_secs.split(":")
    if int(now_min_secs[1]) == 0 and flag_zero_seconds == False:
        print(now_min_secs, datetime.utcnow().strftime("%M:%S"))
        flag_zero_seconds = True

        parsivel.write('CS/M/S/SFs:%01,%02,%03,%04,%05,%06,%07,%08,%09,%10,%11,%12,%13,%14,%15,%16,%17,%18,%20,%21,%22,%23,%24,%25,%26,%27,%28,%30,%31,%32,%33,%34,%35,%60,\nF90:%90,\nF91:%91,\nF93:%93,\nF61:%61;\r\n'.encode('utf-8'))
        sleep(1) # can i remove this ?
        parsivel.write('CS/P\r\n'.encode('utf-8'))
        telegram_single_values=parsivel.readlines()
        for index, item in enumerate(telegram_single_values):
            print(index, item)
        print('\n')

    elif int(now_min_secs[1]) != 0 and flag_zero_seconds == True:
        # once we passed 00secs 
        # reset flag_zero_seconds
        flag_zero_seconds = False
    sleep(1)


   
    # TODO: check how field 61 is written 

    # print('telegram_single_values:', telegram_single_values)

    # parsivel.write('CS/M/S/%90,\r\n'.encode('utf-8'))
    # sleep(1)
    # parsivel.write('CS/P\r\n'.encode('utf-8'))
    # f90_values=parsivel.readlines()
    # print('f90_values:', f90_values)

    # parsivel.write('CS/M/S/%91,\r\n'.encode('utf-8'))
    # sleep(1)
    # parsivel.write('CS/P\r\n'.encode('utf-8'))
    # f91_values=parsivel.readlines()
    # print('f91_values:', f91_values)

    # parsivel.write('CS/M/S/%93,\r\n'.encode('utf-8'))
    # sleep(1)
    # parsivel.write('CS/P\r\n'.encode('utf-8'))
    # f93_values=parsivel.readlines()
    # print('f93_values:', f93_values)

    # parsivel.write('CS/M/S/%61,\r\n'.encode('utf-8'))
    # sleep(1)
    # parsivel.write('CS/P\r\n'.encode('utf-8'))
    # f61_values=parsivel.readlines()
    # print('f61_values:', f61_values)

# how to get the values at the same moment, so there is no time discrepancy?
