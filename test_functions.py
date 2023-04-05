import json
from pathlib import Path
from  modules.util_functions import yaml2dict, capture_telegram_prfx_vars, create_logger

wd = Path(__file__).parent 
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


def test_logger():
    logger = create_logger(log_dir=Path(config_dict['log_dir']), 
                        script_name=config_dict['script_name'], 
                        parsivel_name=config_dict['global_attrs']['sensor_name'])
    logger.info(msg=f"Testing logger in {__file__}")
    assert logger.name == f"{config_dict['script_name']}: {config_dict['global_attrs']['sensor_name']}"

    log_file = Path(config_dict['log_dir']) / 'log.json'
    with open(log_file, 'r') as log_file_r:
        last_log_line = log_file_r.readlines()[-1]
        last_log_line = (json.loads(last_log_line))
        assert last_log_line['name'] == f"{config_dict['script_name']}: {config_dict['global_attrs']['sensor_name']}"
        assert last_log_line['msg'] == f"Testing logger in {__file__}"

