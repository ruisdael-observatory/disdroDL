import pandas as pd
from pathlib import Path
from typing import Dict
from datetime import datetime
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


def str2list_by_ndigits(input: str, ndigits: int) -> list[str]: 
    '''
    converts str (sequence of characters) into a list,
    with each item being ndigits long.
    Used only for F93 values, when they are in  '00000000000' (Ruisdael CSVs) 
    '''
    range_obj = range(0, len(input), ndigits)
    list_val = [input[i:i + ndigits] for i in range_obj]
    return list_val


def telegram_list2dict(telegram_indeces: list, telegram: list) -> Dict:
    '''
    Converts the parsivel telegram list to a dictionary.
    The dictionary keys are the iter numbers of the telegram string 
    The telegram list input: ['0000.102', '0100.87', '57', '58', '-RADZ', ' RL-'
    Telegram has the following sequence: 01,02,03...35,60,90,91,93
    '''
    telegram_dict = {key: None for key in telegram_indeces}
    # print(telegram[:-3])
    for index, field_n in enumerate(telegram_indeces[:-3]):  # ignore fields 90,91,93
        telegram_dict[field_n] = telegram[index]
    telegram_dict['90'] = (",").join(telegram[-65:-33])
    telegram_dict['91'] = (",").join(telegram[-33:-1])
    telegram_dict['93'] = telegram[-1]
    return telegram_dict


def csv2df(csv_path: str) -> pd.DataFrame:
    '''
    imports CSV file content on Pandas dataframe.
    pd.read_csv arguments' values are set for Ruisdael parsivel CSVs
    '''
    b2str = lambda x: x[2:-1]  # rm literal "b'...'" from csv telegram 
    df = pd.read_csv(csv_path,
                     sep=';',
                     header=0,
                     names=['datetime', 'timestamp', 'telegram'],  # 'fieldV', 'fieldN', 'raw_data'],
                     dtype={'datetime': 'string', 'timestamp': 'Float64'},
                     converters={'telegram': b2str},
                     parse_dates=['datetime'])
    return df


def telegram2dict(telegram: str, dt: datetime, ts: float, ) -> pd.DataFrame:
    '''
    Creates 1 dict from a dataframe row, with the telegram values
    '''
    telegram_str = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%19;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;%90;%91;%93'
    telegram_indeces = telegram_str.replace('%', '').split(';')  # 38 fields
    telegram_dict = telegram_list2dict(telegram_indeces=telegram_indeces,
                                       telegram=telegram.split(';'))
    telegram_dict['datetime'] = dt
    telegram_dict['timestamp'] = ts
    return telegram_dict


if __name__ == '__main__':
    df = csv2df(csv_path='sample_data/sample_20231106_PAR007_CabauwTower.csv')
    for index, csv_row in df.iterrows():
        print(index)
        telegram_dict = telegram2dict(telegram=csv_row['telegram'],
                                      dt=csv_row['datetime'],
                                      ts=csv_row['timestamp'], )
        telegram = Telegram(config_dict=config_dict,
                            telegram_lines=None,
                            telegram_data=telegram_dict,
                            timestamp=telegram_dict['datetime'],
                            data_dir=wd / 'sample_data',  # change
                            data_fn_start='test',  # TODO: fn_start = f"{now_utc.ymd}_{site_name}-{st_code}_{sensor_name}"
                            logger=logger
                            )
        telegram.str2list(field='90', separator=',')
        telegram.str2list(field='91', separator=',')
        telegram.telegram_data['93'] = str2list_by_ndigits(input=telegram.telegram_data['93'], ndigits=3)
        telegram.append_data_to_netCDF()

'''

# * cmd args: input, date, config, (output file, print)
# * field 93 error handling: what happens when x is present 
'''
