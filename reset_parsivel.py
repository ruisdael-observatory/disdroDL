from pathlib import Path
from modules.util_functions import create_logger, yaml2dict, init_serial, parsivel_reset


print(__file__)
wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')
logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                       script_name=config_dict['script_name'], 
                       parsivel_name=config_dict['Parsivel_name'])
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)  # initiate serial connection
parsivel_reset(serialconnection=parsivel, logger=logger)
parsivel.close()

# parsivel.reset_input_buffer()  # Flushes input buffer


# parsivel.write(parsivel_sample_interval)
# parsivel.write(parsivel_set_station_name)
# parsivel.write(parsivel_set_ID)
# # parsivel.write(parsivel_request_field_91)
# parsivel.write(parsivel_set_real_time)   
# # parsivel.write(parsivel_restart)
# parsivel.write('CS/R/19\r'.encode('utf-8')) # date and time start
# parsivel.write(parsivel_pooling_mood) # set polling mode: requires active request of telegram
# sleep(2)
# parsivel.write(parsivel_set_telegram_list) # Writes the parsivel user telegram string to the Parsivel


# parsivel.write(parsivel_current_configuration) # ask parsivel for config
# for config_line in parsivel.readlines(): # print config
#     print(config_line)

# parsivel.close()