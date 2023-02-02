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

# sleep(1)
# parsivel.reset_input_buffer()  # Flushes input buffer
# sleep(1)
# sleep(1)
while True:
    try:
        print('-- inside loop --')
        parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'])
        # parsivel.write(parsivel_set_telegram_list) # Writes the parsivel user telegram string to the Parsivel
        sleep(1)
        parsivel.write(parsivel_pooling_mood)
        output=parsivel.readline()
        # print(output, len(output))

        output_break_list = binary2list(binarystr=output, spliter='BREAK')
        print('output_break_list len:', len(output_break_list))
        if len(output_break_list) > 1 and 'OK' not in output_break_list[0]:
            print('output_break_list[0]:', output_break_list[0])
            print('output_break_list[1]:', (output_break_list[1])[0:20], 'len:', len(output_break_list[1]))
            print('output_break_list[2]:', (output_break_list[2])[0:20], 'len:', len(output_break_list[2]))
            print('output_break_list[3]:', (output_break_list[3])[0:20], 'len:', len(output_break_list[3]))
            print('output_break_list[4]:', output_break_list[4]) # WARNING: only 1 entry is shown

        #     for item in output_break_list:
        #         print(item[0:50], '...')
        #     # print(output_break_list)
        #     print(len(output_break_list))
        #     break
        parsivel.close()
        sleep(60)
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
            # logger.error(msg=e.message)
        else:
            print(e)

# let me try to work with readlines



# parsivel.write(parsivel_sample_interval)
# sleep(1)

# parsivel_str_list = []
# while True:
#     parsivel.write('CS/R\r'.encode('utf-8')) # request telegram
#     parsivel_lines = parsivel.readlines() 
#     print(len(parsivel_lines))
#     if len(parsivel_lines) > 1:
#         print(parsivel_lines)
#         parsivel_str_list = binary2list(binarystr=parsivel_lines[2], spliter=';')
#         print(parsivel_str_list, '\b', 'list size:', len(parsivel_str_list))

#         # sleep(2)
#         # print('F61:')
#         # parsivel.write(parsivel_request_field_61)
#         # parsivel_lines = parsivel.readlines() 
#         # print(parsivel_lines)
#         break
#     sleep(1)
# print('end')
parsivel.close()