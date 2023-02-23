import csv
import os
from datetime  import datetime
from modules.util_functions import capture_telegram_prfx_vars

class NowTime:
    '''
    Class dedicated to represent current date and time in different formats
    Attributes:
        utc : datetime object representing class instance time of instantiation
        time_list : list of hour,minutes,seconds of time of instantiation time
    '''
    def __init__(self):
        self.utc = datetime.utcnow()
        self.time_list = (self.utc.strftime("%H:%M:%S")).split(":")  # used to be: now_hour_min_secs
        # now_hour_min_secs = now_hour_min_secs.split(":")
    def date_strings(self):
        '''
        def Converts instantiation time to different format class attributes
            iso: instantiation time in ISO 8601 format string
            ym: instantiation time YearMonth (YYYYmm) format string 
            ymd: instantiation time YearMonthDay (YYYYmmdd) format string 

        '''
        self.iso = self.utc.isoformat()
        self.ym = self.utc.strftime("%Y%m")
        self.ymd = self.utc.strftime("%Y%m%d")

class Telegram:
    '''
    Class dedicated to handling the returned telegram lines:
        storing, processing and writing to CSV
    Note: f61 is handled a little differently as its values are multi-line, hence self.f61_rows
    
    Methods:
        * create_csv_headers()
        * capture_prefixes_and_data()
        * append_data_to_csv()
    '''
    def __init__(self, telegram_lines, timestamp, data_dir, data_fn_start):
        self.telegram_lines = telegram_lines
        self.timestamp = timestamp
        self.svfs_values = None
        self.svfs_headers = []
        self.f90_values = None
        self.f91_values = None
        self.f93_values = None
        self.f61_values = None
        self.f61_rows = []
        self.f61_headers = []
        self.delimiter = ';'
        self.data_dir = data_dir  
        self.data_fn_start = data_fn_start 
        # data_fn_start shared filename start str, based on date_location_parsivelcode_
        # ie. 20230221_Delft-GV_PAR008_  *.csv

    def create_csv_headers(self, sfvs_telegram_resquest, config_dict):
        '''def Creates the headers to CSV of F61 and SVFS
            config.yml telegram_fields name and unit are used
            adds them to self.f61_headers & self.svfs_headers variables
        '''
        # SVFS
        headers_numbers = ((sfvs_telegram_resquest.replace('%','')).split(';'))[:-1]
        headers_names = []
        for key in headers_numbers:
            header = f"{config_dict['telegram_fields'][key]['name']}"
            if 'unit' in config_dict['telegram_fields'][key].keys():
                header = f"{header} ({config_dict['telegram_fields'][key]['unit']})"
            headers_names.append(header)
        self.svfs_headers = ['timestamp'] + headers_names 
        # F61
        self.f61_headers = [
            'timestamp',
            f"{config_dict['telegram_fields']['61size']['name']} ({config_dict['telegram_fields']['61size']['unit']})",
            f"{config_dict['telegram_fields']['61speed']['name']} ({config_dict['telegram_fields']['61speed']['unit']})"
            ]                    

    def capture_prefixes_and_data(self):
        '''
        def Captures the prefixes and data returned by telegram
        and adds data to appropriate (determined by prefix) self.*_values variable.
        '''
        for telegram_line in self.telegram_lines:
            prefix, values = capture_telegram_prfx_vars(telegram_line=telegram_line)
            if prefix and len(values) > 1 and prefix == 'F61':  # len(values) > 1 since ";" can be captured without values
                self.f61_values = join_f61_items(telegram_list=self.telegram_lines)
                for f61_item in self.f61_values:
                    f61_item_pair = string2row(timestamp=self.timestamp, valuestr=f61_item, delimiter=self.delimiter, prefix=prefix)
                    self.f61_rows.append(f61_item_pair) 
            elif prefix in ['SVFS', 'F90', 'F91', 'F93'] and values:
                prefix_lcase = prefix.lower()
                super(Telegram, self).__setattr__(f'{prefix_lcase}_values', 
                                                  string2row(timestamp=self.timestamp, valuestr=values, delimiter=self.delimiter, prefix=prefix))
    def append_data_to_csv(self, prefix):
        '''
        def Writes headers and appends data from self.*_values to corresponding CSV
        using the self.data_dir and prefix to construct the path + file name.
        In cases of multiline values (F61) several rows are written
        '''
        prefix_lcase = prefix.lower()
        fn = f'{self.data_fn_start}_{prefix}.csv'
        # write headers to csv
        if f'{prefix_lcase}_headers' in self.__dir__() and not os.path.exists(self.data_dir / fn):
            # if headers variable exists and file does not exist
            with open(self.data_dir / fn, "w") as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                writer.writerow(self.__dict__[f'{prefix_lcase}_headers'])
        # write data
        if prefix == 'F61':
            data = self.__dict__[f'{prefix_lcase}_rows']
        else: 
            data = self.__dict__[f'{prefix_lcase}_values']  # prefix will determine what var will be used
        print(prefix, data)
        if len(data) > 0:  # prevent empty data to be written
            with open(self.data_dir / fn, "a") as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                if type(data[0]) == list:
                    for data_item in data:
                        writer.writerow(data_item)
                elif type(data[0]) == str:
                    writer.writerow(data)


def join_f61_items(telegram_list):
    '''
    def uses the telegram_list index, of where F61 is positioned
    to mark th start of F61 items in telegram_list.
    Those items (with exception iog last, empty item) are return in the list of string f61_items

    Each one of the f61_items will be a row, with 2 columns (3 if we include timestamp).
    '''
    for index, item in enumerate(telegram_list):
        if 'F61:' in item.decode('utf-8'):
            f61_items = telegram_list[index:-1]  
            f61_items = [item.decode('utf-8').replace('\r\n', '').replace('F61:','') for item in f61_items]
            f61_items = f61_items
    return f61_items

def string2row(timestamp, valuestr, delimiter, prefix):
    '''
    Converts a telegram string to a list of values, separated by the delimiter 
    and added timestamp to first item.
    The output is ready to be written to CSV 
    '''
    values_list = (valuestr.replace(f'{prefix}:', '')).split(delimiter)        
    values_list = [timestamp] + values_list
    if values_list[-1] == '' or values_list[-1] == '\n':
        values_list = values_list[:-1]  
    return values_list



if __name__ == '__main__':
    now = NowTime()
    print(now.__doc__)
    print(now, now.__dict__, now.utc, now.time_list)
    print(type(now.utc))
    now.date_strings()
    print(now.ymd)
    print(type(now.iso))


