from datetime import datetime
from pprint import pprint
from pathlib import Path
from modules.classes import NowTime, Telegram
from modules.util_functions import yaml2dict, csv_headers

wd = Path(__file__).parent 
test_data_dir = wd / 'test_data'
config_dict = yaml2dict(path = wd / 'config.yml')
telegram_lines=[b'OK\r\n', 
                b'\n', 
                b'SVFS:0000.000;0000.00;00;00;   NP;   C;-9.999;20000;00059;12773;00000;012;450994;2.11.6;2.11.1;0.50;24.3;0;14:09:59;16.02.2023;;;0000.00;000;025;013;013;00.000;0000.0;0000.00;-9.99;0000.00;0000.00;00000007;\n', 
                b'F90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n', 
                b'F91:00.000;00.000;00.000;00.000;00.000;\n', 
                b'F93:000;000;000;000;000;000;\n', 
                b'F61:00.502;00.853\r\n', 
                b'00.606;02.026\r\n', 
                b'00.550;01.595\r\n', 
                b'00.521;01.237\r\n', 
                b'00.540;01.070\r\n', 
                b'00.559;01.710\r\n', 
                b'00.571;01.572\r\n', 
                b';']
svfs = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;'

def test_NowTime():
    now = NowTime()
    test_time_list = datetime.utcnow().strftime("%H:%M:%S").split(":") 
    assert type(now.time_list) == list
    assert now.time_list[0] == test_time_list[0] and now.time_list[1] == test_time_list[1] and now.time_list[2] == test_time_list[2]
    # assert: the following attributes are only created after method: date_strings()
    assert 'iso' not in now.__dict__.keys() and 'ym' not in now.__dict__.keys() and 'ymd' not in now.__dict__.keys() 
    now.date_strings()
    assert 'iso' in now.__dict__.keys() and 'ym' in now.__dict__.keys() and 'ymd' in now.__dict__.keys() 
    assert type(now.iso) == str and type(now.ym) == str and type(now.ymd) == str  


def test_Telegram():
    now = NowTime()
    now.date_strings()
    fn_prefix = 'classtest'
    telegram = Telegram(telegram_lines=telegram_lines, 
                        timestamp=now.iso, 
                        data_dir=test_data_dir,
                        data_fn_prefix=fn_prefix)
    telegram.f61_headers = ['timestamp', 
                            f"{config_dict['telegram_fields']['61size']['name']} ({config_dict['telegram_fields']['61size']['unit']})", 
                            f"{config_dict['telegram_fields']['61speed']['name']} ({config_dict['telegram_fields']['61speed']['unit']})"]                    
    assert telegram.f61_headers == ['timestamp',
                                    f"{config_dict['telegram_fields']['61size']['name']} ({config_dict['telegram_fields']['61size']['unit']})", 
                                    f"{config_dict['telegram_fields']['61speed']['name']} ({config_dict['telegram_fields']['61speed']['unit']})"]
    telegram.svfs_headers = csv_headers(sfvs_telegram_resquest=svfs, config_dict=config_dict)                   
    assert telegram.svfs_headers[0:3] == ['timestamp',
                                          f"{config_dict['telegram_fields']['01']['name']} ({config_dict['telegram_fields']['01']['unit']})", 
                                          f"{config_dict['telegram_fields']['02']['name']} ({config_dict['telegram_fields']['02']['unit']})"] 
    telegram.capture_prefixes_and_data()
    pprint(telegram.__dict__)
    assert telegram.f61_rows[0][1] == '00.502' and telegram.f61_rows[0][2] ==  '00.853'
    assert len(telegram.f61_rows[0]) == (len(telegram.f61_headers))
    assert telegram.svfs_values[1] == '0000.000'
    assert len(telegram.svfs_values) == len(telegram.svfs_headers)
    assert telegram.f90_values[1] == '-9.999'
    assert telegram.f91_values[1] == '00.000'
    assert telegram.f93_values[1] == '000'
    csv_test(telegram=telegram, fn_prefix=fn_prefix, prefix='SVFS', data_dir=test_data_dir, now_iso=now.iso)
    csv_test(telegram=telegram, fn_prefix=fn_prefix, prefix='F90', data_dir=test_data_dir, now_iso=now.iso)
    # csv_test(telegram=telegram, fn_prefix=fn_prefix, prefix='F61', data_dir=test_data_dir, now_iso=now.iso)  # TODO: F61 

def csv_test(telegram, fn_prefix, prefix, data_dir, now_iso):
    telegram.append_data_to_csv(prefix=prefix)
    test_csv_path = data_dir / f'{fn_prefix}_{prefix}.csv'
    lastrow = get_row(csv_path=test_csv_path, row_number=-1)
    assert lastrow[0] == now_iso

    # TODO: more tests
    # TODO: test headers of f61 and svfs
    if prefix == 'SVFS' or prefix == 'F61':
        csv_headers = get_row(csv_path=test_csv_path, row_number=0)
        assert len(lastrow) == len(csv_headers)
        assert csv_headers[0:3] == telegram.svfs_headers[0:3]
 
def get_row(csv_path, row_number):
    with open(csv_path, 'r') as f:
        last_row = f.readlines()[row_number].split(';')
        return last_row

#     with open(csv_path, 'r') as f:
#         f_lines_len = len(list(f))
#         for n, row in enumerate(f):
#             row_list = row.split(';')
#             print(n, row_list)
#             if n == (f_lines_len - 1):  
#                 return last_lin# last item

    # with open(test_data_dir / csvs_suffixes['F61'], "r") as f:
    #     print(f)
    #     for n, row in enumerate(f):
    #         row_list = row.split(';')
    #         print(n, row_list)
    #         if n == 0:
    #             assert row_list[0] == '2023-02-16T14:10:00.966776' 
    #             assert row_list[1] == '00.502' 
    #             assert row_list[2] == '00.853\n' #TODO: remove \n