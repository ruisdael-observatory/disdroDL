""""
This script exports .csv's to netCDF files. It parses the data read from the csv here with custom functions, 
as the functions from the telegram object didn't work on the string of data from the csv.
It then makes a telegram object with the parsed data already inserted, before it gets passed on to a NetCDF object.
"""
import csv
import math
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


def choose_sensor(input: str) -> str:
    '''
    Choose a sensor based on the input string
    '''
    sensors = telegrams.keys()
    '''
    Checks 
    '''
    return next((sensor for sensor in sensors if (sensor in input)), None)



def parsival_telegram_to_dict(telegram: list[str], dt: datetime, ts: datetime, config_dict: Dict):
    '''
    Creates 1 dict from a dataframe row representing a parsivel telegram, with the telegram values
    '''
    default_telegram_indeces = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
    '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '30',
    '31', '32', '33', '34', '35', '60', '90', '91', '93']
    telegram_dict = {}
    x = 0
    for i, key in enumerate(default_telegram_indeces):
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
    return parser.parse_args()            

if __name__ == '__main__':
    '''
    Main script for parsing a csv of telegram
    '''
    args = parse_arguments()
    input_path = Path(args.input)

    sensor = choose_sensor(args.input)
    if sensor is None:
        raise ValueError("Sensor not recognized. Please check the input file name.")

    
    argument_file_path = args.input.split("/")
    #Get destination directory from file path
    directory = argument_file_path[-2]
    #Get date from file path
    get_date = argument_file_path[-1].split("_")[0]
    date = datetime(int(get_date[:4]), int(get_date[4:6]), int(get_date[6:8]))
    ## Config
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / config_files[sensor])
    config_dict_site = yaml2dict(path=wd / args.config)
    config_dict = deep_update(config_dict, config_dict_site)
    conf_telegram_fields = config_dict['telegram_fields']  # multivalue fileds have > 1 dimension
    ## Logger
    # import pdb; pdb.set_trace()
    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=Path(__file__).name,
                           sensor_name=config_dict['global_attrs']['sensor_name'])
    # output file
    site_name = config_dict['global_attrs']['site_name']
    st_code = config_dict['station_code']
    sensor_name = config_dict['global_attrs']['sensor_name']
    output_fn = f"{input_path.stem}"
    output_path = input_path.parent / output_fn
    
    #iterate over all telegrams
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

    #create NetCDF
    nc = NetCDF(logger=logger,
                config_dict=config_dict,
                data_dir=directory,
                fn_start=output_fn,
                full_version=True,
                telegram_objs=telegram_objs,
                date=date)
    
    nc.create_netCDF()
    nc.write_data_to_netCDF_parsivel() if sensor == 'PAR' else nc.write_data_to_netCDF_thies() 
    nc.compress()
