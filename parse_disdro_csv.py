import yaml
import pandas as pd
from pathlib import Path
from typing import Dict
from modules.classes import Telegram
from modules.util_functions import yaml2dict, create_logger
from pydantic.v1.utils import deep_update




wd = Path(__file__).parent
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general.yml')
config_dict_site = yaml2dict(path=wd / 'configs_netcdf' / 'config_007_CABAUW.yml') 
config_dict = deep_update(config_dict, config_dict_site)
conf_telegram_fields = config_dict['telegram_fields']  # multivalue fileds have > 1 dimension

logger = create_logger(log_dir=Path(config_dict['log_dir']),
                       script_name=config_dict['script_name'],
                       parsivel_name=config_dict['global_attrs']['sensor_name'])

telegram_str = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%19;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;%90;%91;%93'
telegram_str = telegram_str.replace('%', '').split(';')  # 38 fields
b2str = lambda x: x[2:-1]  # because pd resconzines telegram as str that start with b'...'

# str(x).decode('ascii')
# seperate telegram from datetime and timestamp
df = pd.read_csv('sample_data/20231106_PAR007_CabauwTower.csv',
                 sep=';',
                 header=0,
                 names=['datetime', 'timestamp', 'telegram'],  # 'fieldV', 'fieldN', 'raw_data'],
                 dtype={'datetime': 'string', 'timestamp': 'Float64'},
                 converters={'telegram': b2str},
                 parse_dates=['datetime'])
# print(df.sample())
telegram_sample = df.at[0, 'telegram']
# print(telegram_sample, type(telegram_sample))


def parse_telegram(telegram: list) -> Dict:
    telegram_dict = {key: None for key in telegram_str}
    for index, field_n in enumerate(telegram_str[:-3]):  # ignore fields 90,91,93
        telegram_dict[field_n] = telegram[index]
    telegram_dict['90'] = telegram[-65:-33]
    telegram_dict['91'] = telegram[-33:-1]
    telegram_dict['93'] = telegram[-1]
    return telegram_dict


# split telegram values; placing each value under the correct column of that row
for index, row in df.iterrows():
    telegram = row['telegram']
    telegram_l = telegram.split(';')
    telegram_dict = parse_telegram(telegram=telegram_l)
    for key, value in telegram_dict.items():
        if key not in ['90', '91']:
            df.loc[index, key] = value
        else:
            df.loc[index, key] = (",").join(value)

df.drop(columns=['telegram'], inplace=True)
df.to_csv(path_or_buf="tmp.csv", sep=";")  # check data in tmp.csv
# TODO: write df to netCDF


## loop through df rows
# at each row add data to self.telegram_data[field] = value
for index, row in df.iterrows():
    # 1 telegram instance per row 
    telegram = Telegram(config_dict=config_dict,
                        telegram_lines=None,
                        telegram_data=row.to_dict(),
                        timestamp=row['datetime'],
                        data_dir=wd / 'sample_data',  # change
                        data_fn_start='test',  # TODO: fn_start = f"{now_utc.ymd}_{site_name}-{st_code}_{sensor_name}"
                        logger=logger
                        )
    # telegram.append_data_to_netCDF()
    # import pdb; pdb.set_trace()

# HOw is time handled?? 
'''
Traceback (most recent call last):
  File "/home/acastro/Documents/projects/parsivel-distrometer-datalogger/parse_disdro_csv.py", line 78, in <module>
    telegram.append_data_to_netCDF()
  File "/home/acastro/Documents/projects/parsivel-distrometer-datalogger/modules/classes.py", line 109, in append_data_to_netCDF
    netCDF_var_time = netCDF_rootgrp.variables['time']
KeyError: 'time'

why is time not a variable from netCDF_rootgrp
netCDF_rootgrp.variables['time']

'''