from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict


print(__file__)
wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')


parsivel_telegram_command = 'CS/RA\r'.encode('utf-8')  # Asks the Parsivel to read out all fields
parsivel_request_field_61 = 'CS/R/61\r'.encode('utf-8')  # Asks the Parsivel to read out field 61
parsivel_request_field_90 = 'CS/R/91\r'.encode('utf-8')  # Asks the Parsivel to read out field 61
parsivel_command_list = 'CS/?\r'.encode('utf-8')  # Reads out a list of serial commands for the Parsivel.
parsivel_ott_telegram = 'CS/M/M/0\r'.encode('utf-8')  # The Parsivel broadcasts the OTT telegram.
parsivel_telegram_start = 'CS/*/D/0\r'.encode('utf-8')  # The Parsivel broadcasts the OTT telegram.
parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')  # The Parsivel broadcasts the user defined telegram. # DONE = MIGRATED TO SCRIPTS
parsivel_set_telegram_list = 'CS/M/S/%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%19;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;%90;%91;%93\r'.encode('utf-8')  # Defines which fields are in the telegram # DONE = MIGRATED TO SCRIPTS
parsivel_current_configuration = 'CS/L\r'.encode('utf-8')  # Outputs current configuration  # DONE = MIGRATED TO SCRIPTS
parsivel_impulse_mode = 'CS/I/60\r'.encode('utf-8')  # Turns poll mode off
parsivel_set_station_name = ('CS/K/' + config_dict['station_name'] + '\r').encode('utf-8')  # Sets the name of the Parsivel, maximum 10 characters
parsivel_set_ID = ('CS/J/' + config_dict['Parsivel_ID'] + '\r').encode('utf-8')  # Sets the ID of the Parsivel, maximum 4 numerical characters
parsivel_reset_factory_settings = 'CS/F/1\r'.encode('utf-8')  # Resets the Parsivel to factory settings.
parsivel_set_real_time = ('CS/U/' + datetime.utcnow().strftime("%d.%m.%Y ") + datetime.utcnow().strftime("%H =%M =%S") + '\r').encode('utf-8')
parsivel_restart = 'CS/Z/1\r'.encode('utf-8')

