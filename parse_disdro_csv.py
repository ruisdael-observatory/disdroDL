""""
This script exports .csv's to netCDF files. It parses the data read from the csv here with custom functions, 
as the functions from the telegram object didn't work on the string of data from the csv.
It then makes a telegram object with the parsed data already inserted, before it gets passed on to a NetCDF object.
"""
import csv
import os
from pathlib import Path
from typing import Dict
from datetime import datetime, timezone
from argparse import ArgumentParser
from pydantic.v1.utils import deep_update
from modules.telegram import ParsivelTelegram, ThiesTelegram, create_telegram
#from pprint import pprint
from modules.util_functions import yaml2dict, create_logger
from modules.netCDF import NetCDF

#Different dictionaries to select the necessary method/file needed, corresponding to the respective sensor
telegrams = {'THIES': ThiesTelegram, 'PAR': ParsivelTelegram}
config_files = {'THIES': 'config_general_thies.yml', 'PAR': 'config_general_parsivel.yml'}
field_type = {'i4': int, 'i2': int, 'S4': str, 'f4': float}

default_parsivel_telegram_indices = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
    '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '30',
    '31', '32', '33', '34', '35', '60', '90', '91', '93']

def choose_sensor(input: str) -> str:
    '''
    Choose a sensor based on the input string
    '''
    sensors = telegrams.keys()
    '''
    Check if the input string is in the list of sensors
    '''
    for sensor in sensors:
        if sensor in input:
            return sensor
        
    return None



def parsival_telegram_to_dict(telegram: list[str], dt: datetime, ts: datetime, config_dict: Dict):
    '''
    Creates 1 dict from a dataframe row representing a parsivel telegram, with the telegram values
    '''

    telegram_dict = {}
    x = 0
    for i, key in enumerate(default_parsivel_telegram_indices):
        if(key == '90' or key == '91'):
            '''
            Field 90 and 91 have a list of 32 values
            Grab the corresponding 32 values for field 90 or 91
            '''
            value_type = field_type[config_dict[key]['dtype']] #Get value type, e.g float or integer
            telegram_value = telegram[-65:-33] if key == '90' else telegram[-33:-1] #Copy all values and cast to respective type
            telegram_dict[key] = [value_type(value) for value in telegram_value]
        elif(key == '93'):
            '''
            Key 93 is a long string of values, not seperated by a semicolon or something else
            Each substring of 3 character is a single value, so a list is created each three characters
            '''
            s = telegram[-1]

            raw_data = [int(s[i:i+3]) for i in range(0, len(s), 3)] #value should always be cast to int
            telegram_dict[key] = raw_data
        else:
            '''
            Value is cast to type based on the config dict
            '''
            #print(i, key, telegram[i])
            telegram_value = field_type[config_dict[key]['dtype']](telegram[i])
            telegram_dict[key] = telegram_value
    
    telegram_dict['datetime'] = dt
    telegram_dict['timestamp'] = str(ts)
    return telegram_dict

def thies_telegram_to_dict(telegram: list[str], dt: datetime, ts: datetime, config_dict: Dict) -> Dict:
    '''
    Creates 1 dict from a dataframe row representing a Thies telegram, with the telegram values
    '''
    telegram_indices = list(config_dict.keys())[1:]
    telegram_dict = {}
    for index, field_n in enumerate(telegram_indices):
        if(field_n == '81'):
            telegram_dict[field_n] = [int(x) for x in telegram[index:index+439]]
        elif(field_n > '520'):
            telegram_dict[field_n] = field_type[config_dict[field_n]['dtype']](telegram[index+439])
        else:
            telegram_dict[field_n] = field_type[config_dict[field_n]['dtype']](telegram[index])
    telegram_dict['2'] = telegram_dict['2'].split(',')[-1]
    telegram_dict['datetime'] = dt
    
    telegram_dict['timestamp'] = str(ts)
    return telegram_dict

def process_txt_row(txt_list: list, config_dict: dict):
    
    telegram_dict = {}
    fields = config_dict.keys()
    for field in txt_list:
        key_value = field.split(':')
        if len(key_value) == 2:
            
            key, value = key_value
            if key in fields:
                data_type = field_type[config_dict[key]['dtype']]
                if key == '90' or key == '91' or key == '93':  
                    list_values = value.split(';')
                    list_values.remove('')
                    telegram_dict[key] = [data_type(x) for x in list_values]
                else:
                    telegram_dict[key] = data_type(value)

    field_20 = txt_list[20].split(':')
    field_21 = txt_list[21].split(':')
    date = field_21[1] + field_20[1] + field_20[2] + field_20[3]
    timestamp = datetime.strptime(date, "%d.%m.%Y%H%M%S")

    telegram_dict['timestamp'] = str(timestamp)
    telegram_dict['datetime'] = datetime.fromtimestamp(timestamp.timestamp(), tz=timezone.utc)
    return telegram_dict, timestamp

def process_row(csv_list: list, sensor: str, config_dict: dict):
    '''
    Determines which in which format the csv is in, and preprocesses if necessary, currently able to parse 4 csv formats:
    Parsivel-> one format where all values from a telegram are contained in a single column in a string, or each value in their own column
    Thies-> one format where all values from a telegram are contained in a single column in a string, or each value in their own column
    All formats don't indicate when a value is part of a list, this is hardcoded based ont the respective documentation
    '''
    if len(csv_list) == 3:
        #If the telegram consists of 3 columns, the
        dt_str, ts_str, telegram_b = csv_list
        timestamp = datetime.strptime(dt_str, "%Y%m%d-%H%M%S")
        date = datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
        if sensor == 'PAR':
            telegram = telegram_b[2:-1].split(";")
            return parsival_telegram_to_dict(telegram, date, timestamp, config_dict), timestamp
        else: #Thies
            telegram = telegram_b[4:-1].split(";")
            return thies_telegram_to_dict(telegram, date, timestamp, config_dict), timestamp
    else:
        if sensor == 'PAR':
            date = csv_list[0]
            timestamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
            return parsival_telegram_to_dict(csv_list[1:], date, timestamp, config_dict), timestamp
        else: #Thies
            dates = csv_list[0].split(",")
            timestamp = datetime.strptime(dates[0], "%Y%m%d-%H%M%S")
            date = datetime.fromtimestamp(float(csv_list[1]), tz=timezone.utc)
            return thies_telegram_to_dict(csv_list, date, timestamp, config_dict), timestamp



def txt_loop(input_path: Path, sensor: str, config_dict: dict, conf_telegram_fields: dict, logger):
    for file in os.listdir(input_path):
        if file.endswith(".txt"):
            telegram_objs = []
            txt_file = open(input_path / file, "r")
            txt_telegram = txt_file.read().splitlines()
            telegram, timestamp = process_txt_row(txt_telegram, conf_telegram_fields)

            telegram_instance = telegrams[sensor](
                config_dict=config_dict,
                telegram_lines="",
                timestamp=timestamp,
                db_cursor=None,
                logger=logger,
                telegram_data=telegram,
            )
            #print(telegram)
            telegram_objs.append(telegram_instance)

    return telegram_objs





def csv_loop(input_path: Path, sensor: str, config_dict: dict, conf_telegram_fields: dict, logger):

    with open(input_path , newline='') as csvfile:  # pylint: disable=W1514
        reader = csv.reader(csvfile, delimiter=';')
        telegram_objs = []
        for row in reader:
            if(row[0] == 'Timestamp (UTC)'):
                continue
            #parse single telegram row from csv
            telegram, timestamp = process_row(row, sensor, conf_telegram_fields)
            #choose telegram object based on sensor
            telegram_instance = telegrams[sensor](
                config_dict=config_dict,
                telegram_lines="",
                timestamp=timestamp,
                db_cursor=None,
                logger=logger,
                telegram_data=telegram,
            )

            telegram_objs.append(telegram_instance)

    return telegram_objs



def parse_arguments():
    '''
    Parse arguments for the script
    '''
    parser = ArgumentParser(
        description="Parser for historical Ruisdael's OTT Parsivel CSVs. Converts CSV to netCDF. \
            Run: python parse_disdro_csv.py -c configs_netcdf/config_007_CABAUW.yml\
                -i sample_data/20231106_PAR007_CabauwTower.csv \
            Output netCDF: store in same directory as input file"
        )
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='Path to site config file. ie. -c configs_netcdf/config_007_CABAUW.yml')
    parser.add_argument(
        '-i',
        '--input',
        required=True,
        help='Path to input CSV file. ie. -i sample_data/20231106_PAR007_CabauwTower.csv')
    parser.add_argument(
        '-f',
        '--file_type',
        required=False,
        default='csv',
        help='File type of the input file(s). ie. -f csv or -f txt')	
    return parser.parse_args() 

def main(args):
    '''
    Main script for parsing a csv of telegram
    '''
    input_path = Path(args.input)
    
    #get date from input file
    get_date = input_path.stem.split('_')[0]
    date = datetime(int(get_date[:4]), int(get_date[4:6]), int(get_date[6:8]))
    ## Config
    wd = Path(__file__).parent
    config_dict_site = yaml2dict(path=wd / args.config)
    sensor_name = config_dict_site['global_attrs']['sensor_name']
    sensor = choose_sensor(sensor_name)

    if sensor is None:
        raise ValueError('Sensor not found in site config file')

    config_dict = yaml2dict(path=wd / 'configs_netcdf' / config_files[sensor])
    config_dict = deep_update(config_dict, config_dict_site)
    conf_telegram_fields = config_dict['telegram_fields']  # multivalue fileds have > 1 dimension
    ## Logger
    # import pdb; pdb.set_trace()
    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=Path(__file__).name,
                           sensor_name=config_dict['global_attrs']['sensor_name'])
    # output file name
    output_fn = f"{input_path.stem}"
    output_directory = input_path.parent

    #iterate over all telegrams
    if args.file_type == 'txt':
        telegram_objs = txt_loop(input_path, sensor, config_dict, conf_telegram_fields, logger)
    else:
        telegram_objs = csv_loop(input_path, sensor, config_dict, conf_telegram_fields, logger)
    print(telegram_objs[0].telegram_data )
    #create NetCDF
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=output_directory,
                fn_start=output_fn,
                full_version=True,
                telegram_objs=telegram_objs,
                date=date)
    
    nc.create_netCDF()
    nc.write_data_to_netCDF_parsivel() if sensor == 'PAR' else nc.write_data_to_netCDF_thies() 
    nc.compress()   

if __name__ == '__main__':
    main(parse_arguments())
