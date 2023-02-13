import csv
from datetime import datetime
from pathlib import Path
from  util_functions import yaml2dict, create_dir, create_new_csv, binary2list, init_serial
from parsivel_cmds import *
from log import log 
from time import sleep

print('starting script')

wd = Path(__file__).parent 
config_dict = yaml2dict(path = wd / 'config.yml')

# set up log
log_dir = Path(config_dict['log_dir'])
created_log_dir = create_dir(log_dir)
log_file = log_dir / 'log.json'
logger = log(log_path=log_file, 
            log_name=f"{config_dict['script_name']}: {config_dict['Parsivel_name']}")  
logger.info(msg=f"Starting {__file__} for {config_dict['Parsivel_name']}")
print(f'{__file__} running\nLogs written to {log_dir}')


# intiated serial connection
parsivel = init_serial(port=config_dict['port'], baud=config_dict['baud'], logger=logger)
parsivel.reset_input_buffer()  # Flushes input buffer
parsivel.write('CS/Z/1\r\n'.encode('utf-8'))  # Restart sensor, reset the rain amount
sleep(10)
parsivel.write('CS/M/M/1\r\n'.encode('utf-8')) # User defined telegram


flag_zero_seconds = False
while True:
    try:
        now_utc = datetime.utcnow()
        now_hour_min_secs = now_utc.strftime("%H:%M:%S")
        now_hour_min_secs = now_hour_min_secs.split(":")
        print(now_hour_min_secs)
        if int(now_hour_min_secs[2]) == 0 and flag_zero_seconds == False:
            print('time to write:', now_hour_min_secs, datetime.utcnow().strftime("%H:%M:%S"))
            flag_zero_seconds = True
            # dates
            now_utc_iso = now_utc.isoformat()
            now_utc_ym = now_utc.strftime("%Y%m")
            now_utc_ymd = now_utc.strftime("%Y%m%d")
            # create dir
            data_dir = Path(config_dict['data_dir']) / now_utc_ym # create monthly data dir
            created_data_dir = create_dir(data_dir)
            if created_data_dir:
                logger.info(msg=f'Created data directory: {data_dir}')

            # request telegram
            svfs = '%01,%02,%03,%04,%05,%06,%07,%08,%09,%10,%11,%12,%13,%14,%15,%16,%17,%18,%20,%21,%22,%23,%24,%25,%26,%27,%28,%30,%31,%32,%33,%34,%35,%60,'
            svfs_prefix = 'SVFs:'  # Single Value Fields; for identification 
            svfs_cmd = 'CS/M/S/' + prefix
            parsivel.write(svfs_cmd + svfs + '\nF90:%90,\nF91:%91,\nF93:%93,\nF61:%61;\r\n'.encode('utf-8'))
            sleep(1)
            parsivel.write('CS/P\r\n'.encode('utf-8'))
            telegram_single_values=parsivel.readlines()

            # create CSV
            headers = (svfs.replace('%','')).split(',')            
            filename = f"{now_utc_ymd}_{config_dict['station_site']}-{config_dict['station_name']}_{config_dict['Parsivel_name']}.csv"
            created_new_csv = create_new_csv(csv_path=data_dir / filename, headers=headers)
            if created_new_csv:
                logger.info(msg=f'Created CSV: {data_dir / filename}')

            for index, item in enumerate(telegram_single_values):
                if index == 2:
                    print(item)
                    parsivel_str_list = binary2list(binarystr=item, spliter=',', prefix=svfs_prefix)
                    with open(data_dir / filename, "a") as f:
                        writer = csv.writer(f, delimiter=";")
                        writer.writerow([now_utc_iso] + parsivel_str_list)

                print(index, item)
            print('\n')


        elif int(now_hour_min_secs[2]) != 0 and flag_zero_seconds == True:
            # once we passed 00secs: reset flag_zero_seconds
            flag_zero_seconds = False
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
            logger.error(msg=e.message)
        else:
            print(e)
    sleep(1)


# TODO:
# * check how field 61 is written 
# * monthly dir creation
# * write to CSV
# * CSV headers
# * write to several CSVs
# * add timestamp to CSV headers