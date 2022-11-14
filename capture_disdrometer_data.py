import time
import csv
from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict, create_dir, create_new_csv, binary2list, init_serial
from parsivel_cmds import *
from log import log 

print('starting script')

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

# set up log
log_dir = wd / config_dict['log_dir']
created_log_dir = create_dir(log_dir)
log_file = log_dir / 'log.json'
logger = log(log_path=log_file, 
            log_name=f"{config_dict['script_name']}: {config_dict['Parsivel_name']}")  
logger.info(msg=f"Starting {__file__} for {config_dict['Parsivel_name']}")
print(f'{__file__} running\nLogs written to {log_dir}')


# # intiated serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
# setup parsivel config commands 
parsivel.write(parsivel_user_telegram) # set up parsivel: to send user defined telegram 
time.sleep(2) 
parsivel.write(parsivel_set_telegram_list)  # set up parsivel: defining list of fields 
time.sleep(2)
parsivel.write(parsivel_current_configuration) # ask parsivel for config
for config_line in parsivel.readlines(): # print config
    logger.info(msg=f'Config: {config_line}')


while True:
    try:
        # time
        now_utc = datetime.utcnow()
        now_utc_iso = now_utc.isoformat()
        now_utc_ymd = now_utc.strftime("%Y%m%d")
        # daily data dirs
        data_dir = wd / config_dict['data_dir'] / now_utc_ymd # set up data dir
        created_data_dir = create_dir(data_dir)
        if created_data_dir:
            logger.info(msg=f'Created data directory: {data_dir}')
        parsivel_set_telegram_list_str = parsivel_set_telegram_list.decode('utf-8')
        parsivel_set_telegram_list_str = parsivel_set_telegram_list_str.replace('CS/M/S/', '').replace('\r','').replace('%', 'Field_')
        headers = ['Timestamp (UTC)']+ parsivel_set_telegram_list_str.split(';')
        filename = f"{now_utc_ymd}_{config_dict['Parsivel_name']}.csv"
        created_new_csv = create_new_csv(csv_path=data_dir / filename, headers=headers)
        # daily CSVs
        if created_new_csv:
            logger.info(msg=f'Created CSV: {data_dir / filename}')
        filename_field_61 = f"{now_utc_ymd}_{config_dict['Parsivel_name']}_field61.csv"
        created_new_csv_f61 = create_new_csv(csv_path=data_dir / filename_field_61, headers=['Timestamp (UTC)','Particle_size', 'Particle_speed'])
        if created_new_csv_f61:
            logger.info(msg=f'Created CSV: {data_dir / filename_field_61}')
        # Telegram processing
        parsivel_lines = parsivel.readlines()  # Reads the output the serial communication
        if len(parsivel_lines) == 1 and len(parsivel_lines[0]) >= 20:
            # single message with all fields, except 61
            parsivel_str_list = binary2list(binarystr=parsivel_lines[0], spliter=';')
            with open(data_dir / filename, "a") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([now_utc_iso] + parsivel_str_list)
            logger.info(msg=f'Written row to {filename}')
            parsivel.write(parsivel_request_field_61)  # request field 61
        elif len(parsivel_lines) > 1:
            # field 61 condition
            with open(data_dir / filename_field_61, "a") as g:  # 61
                writer = csv.writer(g, delimiter=";")
                for line in parsivel_lines:
                    if len(line) > 5 and len(line) < 20:
                        # TODO: process parsivel_lines to str and remove non-printing chars
                        parsivel_str_list = binary2list(binarystr=line, spliter=';')
                        writer.writerow([now_utc_iso] + parsivel_str_list)
                        logger.info(msg=f'Written row to {filename_field_61} {parsivel_str_list}')
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
            logger.error(msg=e.message)
        else:
            print(e)
