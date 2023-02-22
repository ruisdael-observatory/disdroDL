from datetime import datetime
from pathlib import Path
from  modules.util_functions import yaml2dict


wd = Path(__file__).parent.parent 
config_dict = yaml2dict(path = wd / 'config.yml')
parsivel_telegram_command = 'CS/RA\r'.encode('utf-8')  # Asks the Parsivel to read out all fields
parsivel_request_field_61 = 'CS/R/61\r'.encode('utf-8')  # Asks the Parsivel to read out field 61
parsivel_request_field_91 = 'CS/R/91\r'.encode('utf-8')  # Asks the Parsivel to read out field 61
parsivel_command_list = 'CS/?\r'.encode('utf-8')  # Reads out a list of serial commands for the Parsivel.
parsivel_ott_telegram = 'CS/M/M/0\r'.encode('utf-8')  # The Parsivel broadcasts the OTT telegram.
parsivel_telegram_start = 'CS/*/D/0\r'.encode('utf-8')  # Communication Mode": 0=deactivate; 1=activate
parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')  # The Parsivel broadcasts the user defined telegram. # DONE = MIGRATED TO SCRIPTS

parsivel_set_telegram_list = 'CS/M/S/F01:%01;F02:%02;F03:%03;F04:%04;F05:%05;F06:%06;F07:%07;F08:%08;F09:%09;\
F10:%10;F11:%11;F12:%12;F13:%13;F14:%14;F15:%15;F16:%16;F17:%17;F18:%18;\
F20:%20;F21:%21;F22:%22;F23:%23;F24:%24;F25:%25;F26:%26;F27:%27;F28:%28;\
F30:%30;F31:%31;F32:%32;F33:%33;F34:%34;F35:%35;\
F60:%60;F90:%90;F91:%91;F93:%93;\
F61:%61\r'.encode('utf-8')

# parsivel_set_telegram_list = 'CS/M/S/F34:%34;F35:%35;'.encode('utf-8')

# parsivel_set_telegram_list = 'CS/M/S/%01;%02;%03;%04;%05;%06;%07;%08;%61\r'.encode('utf-8')  # Defines which fields are in the telegram # DONE = MIGRATED TO SCRIPTS

parsivel_current_configuration = 'CS/L\r'.encode('utf-8')  # Outputs current configuration  # DONE = MIGRATED TO SCRIPTS
parsivel_sample_interval = 'CS/I/60\r'.encode('utf-8')  # Adjust sample interval and start transfer in seconds; 0=pooling mode
parsivel_sample_interval = 'CS/I/0\r'.encode('utf-8')  # Adjust sample interval and start transfer in seconds; 0=pooling mode
parsivel_set_station_name = ('CS/K/' + config_dict['station_name'] + '\r').encode('utf-8')  # Sets the name of the Parsivel, maximum 10 characters
parsivel_set_ID = ('CS/J/' + config_dict['Parsivel_ID'] + '\r').encode('utf-8')  # Sets the ID of the Parsivel, maximum 4 numerical characters
parsivel_reset_factory_settings = 'CS/F/1\r'.encode('utf-8')  # Resets the Parsivel to factory settings.
parsivel_set_real_time = ('CS/U/' + datetime.utcnow().strftime("%d.%m.%Y ") + datetime.utcnow().strftime("%H =%M =%S") + '\r').encode('utf-8')
parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
parsivel_pooling_mood = 'CS/P\r'.encode('utf-8')
