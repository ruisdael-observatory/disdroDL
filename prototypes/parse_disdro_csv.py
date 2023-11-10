import yaml
import pandas as pd
from pathlib import Path
from typing import Dict
from datetime import datetime

def yaml2dict(path: str) -> Dict:
    with open(path, 'r') as yaml_f:
        yaml_content = yaml_f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    return yaml_dict


wd = Path(__file__).parent.parent
config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_general.yml')
telegram_fields = config_dict['telegram_fields']  # multivalue fileds have > 1 dimension


b2str = lambda x: x[2:-1]  # because pd resconzines telegram as str that start with b'...'

# str(x).decode('ascii')
# seperate telegram from datetime and timestamp
df = pd.read_csv('csvs/20231106_PAR007_CabauwTower.csv',
                 sep=';',
                 header=0,
                 names=['datetime', 'timestamp', 'telegram'],
                 dtype={'datetime': 'string', 'timestamp': 'Float64', 'telegram': 'string'},
                 converters={'telegram': b2str},
                 parse_dates=['datetime'])
print(df.sample())
telegram_sample = df.at[0, 'telegram']
print(telegram_sample, type(telegram_sample))

# # [1439 rows x 3 columns]

# import pdb; pdb.set_trace()
telegram_fields_n = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%19;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;%90;%91;%93'
telegram_fields_n = telegram_fields_n.replace('%', '').split(';') #38 fields

print(telegram_fields_n)
for field_n in telegram_fields_n:
    print(telegram_fields[field_n])

# for field_n, field_metadata in telegram_fields.items():
#     print(field_n, field_metadata)
