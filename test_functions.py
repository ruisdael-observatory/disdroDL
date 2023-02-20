import os
from pathlib import Path
from  modules.util_functions import yaml2dict, capture_telegram_prfx_vars, join_f61_items,string2row, append_csv_row

wd = Path(__file__).parent 
test_data_dir = wd / 'test_data'
csvs_suffixes = {'SVFS':'test_SVFS.csv', 'F90':'test_F90.csv', 'F91':'test_F91.csv', 'F93':'test_F93.csv', 'F61':'test_F61.csv'}
now_utc_iso = '2023-02-16T14:10:00.966776'
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

f61_rows = [['2023-02-16T14:10:00.966776', '00.502', '00.853'],
            ['2023-02-16T14:10:00.966776', '00.606', '02.026'],
            ['2023-02-16T14:10:00.966776', '00.550', '01.595'],
            ['2023-02-16T14:10:00.966776', '00.521', '01.237'],
            ['2023-02-16T14:10:00.966776', '00.540', '01.070'],
            ['2023-02-16T14:10:00.966776', '00.559', '01.710'],
            ['2023-02-16T14:10:00.966776', '00.571', '01.572']]

def test_yaml():
    config_dict = yaml2dict(path = wd / 'config.yml')
    # print(config_dict)
    assert len(config_dict.keys()) > 1


def test_capture_telegram_prfx_vars():
    for n, telegram_line in enumerate(telegram_lines):
        prefix, values = capture_telegram_prfx_vars(telegram_line=telegram_line)
        if n == 2:
            assert prefix == 'SVFS' and values.startswith('0000.000;0000.00')
        elif n == 3:
            assert prefix == 'F90' and values.startswith('-9.999;-9.999;-9.999;')
        elif n == 4:
            assert prefix == 'F91' and values.startswith('00.000;00.000;')
        elif n == 5:
            assert prefix == 'F93' and values.startswith('000;000;000;')
        elif n == 6:
            assert prefix == 'F61' and values.startswith('00.502;00.853') 
            print(prefix, values)


def test_join_f61_items():
    f61_value_items = join_f61_items(telegram_lines)
    f61_rows = []
    print(f61_value_items)
    assert len(f61_value_items) == 7 and f61_value_items[-1] == '00.571;01.572'
    for f61_item in f61_value_items:
        f61row = string2row(timestamp=now_utc_iso, valuestr=f61_item, delimiter=';', prefix='F61')
        f61_rows.append(f61row)
        print(f61row)       
    assert f61_rows[-1][1]  == '00.571' and f61_rows[-1][2] == '01.572'


def test_append_row_f61():
    csv_path = test_data_dir/csvs_suffixes['F61']
    print(csv_path.is_file())
    if csv_path.is_file():
        os.remove(test_data_dir / csvs_suffixes['F61'])
    for row_list in f61_rows:
        append_csv_row(data_dir=test_data_dir, 
                       filename=csvs_suffixes['F61'], 
                       delimiter=';', 
                       data_list=row_list)
    with open(test_data_dir / csvs_suffixes['F61'], "r") as f:
        print(f)
        for n, row in enumerate(f):
            row_list = row.split(';')
            if n == 0:
                assert row_list[0] == '2023-02-16T14:10:00.966776' and row_list[1] == '00.502' and row_list[2] == '00.853\n'
            print(n, row_list)
