import os
import logging
from logging import StreamHandler
from datetime import datetime, timedelta
from pprint import pprint
from pathlib import Path
from modules.classes import NowTime, Telegram
from modules.util_functions import yaml2dict
from netCDF4 import Dataset
from cftime import num2date
from pydantic.v1.utils import deep_update


log_handler = StreamHandler()
logger = logging.getLogger('testlog')
logger.addHandler(log_handler)
wd = Path(__file__).parent 
test_data_dir = wd / 'test_data'
config_dict = yaml2dict(path = wd / 'configs_netcdf' / 'config_general.yml')
config_dict_site = yaml2dict(path = wd / 'configs_netcdf' / 'config_008_GV.yml')
config_dict = deep_update(config_dict, config_dict_site)

parsivel_lines = [b'TYP OP4A\r\n', b'01:0000.000\r\n', b'02:0000.00\r\n', b'03:00\r\n', b'04:00\r\n', b'05:   NP\r\n', b'06:   C\r\n', b'07:-9.999\r\n', b'08:20000\r\n', b'09:00043\r\n', b'10:13894\r\n', b'11:00000\r\n', b'12:021\r\n', b'13:450994\r\n', b'14:2.11.6\r\n', b'15:2.11.1\r\n', b'16:0.50\r\n', b'17:24.3\r\n', b'18:0\r\n', b'19: \r\n', b'20:10:13:21\r\n', b'21:25.05.2023\r\n', b'22:\r\n', b'23:\r\n', b'24:0000.00\r\n', b'25:000\r\n', b'26:032\r\n', b'27:022\r\n', b'28:022\r\n', b'29:000.041\r\n', b'30:00.000\r\n', b'31:0000.0\r\n', b'32:0000.00\r\n', b'34:0000.00\r\n', b'35:0000.00\r\n', b'40:20000\r\n', b'41:20000\r\n', b'50:00000000\r\n', b'51:000140\r\n', b'90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\r\n', b'91:00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;\r\n', b'93:000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;\r\n', b'94:0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;0000;\r\n', b'95:0.00;0.00;0.00;0.00;0.00;0.00;0.00;\r\n', b'96:0000000;0000000;0000000;0000000;0000000;0000000;0000000;\r\n', b'97:;\r\n', b'98:;\r\n', b'99:;\r\n', b'\x03']

def test_NowTime():
    now = NowTime()
    test_time_list = datetime.utcnow().strftime("%H:%M:%S").split(":") 
    assert type(now.time_list) == list
    assert now.time_list[0] == test_time_list[0] and now.time_list[1] == test_time_list[1] and now.time_list[2] == test_time_list[2]
    # assert: the following attributes are only created after method: date_strings()
    assert type(now.iso) == str and type(now.ym) == str and type(now.ymd) == str  

def test_Telegram_netCDF():
    now = NowTime()
    fn_start = 'classtest'
    create_test_data_dir(dir=test_data_dir)
    delete_netcdf(fn_start='classtest', data_dir=test_data_dir,)  # delete old netCDF
    telegram = Telegram(config_dict=config_dict,
                        telegram_lines=parsivel_lines, 
                        timestamp=now.utc, 
                        data_dir=test_data_dir,
                        data_fn_start=fn_start,
                        logger=logger)         
    # test dimensions
    rootgrp = Dataset(f'{test_data_dir/fn_start}.nc', 'r', format="NETCDF4")  # read netcdf
    assert set(['time', 'diameter_classes', 'velocity_classes']).issubset(set(rootgrp.dimensions.keys()))
    netCDF_var_velocity = rootgrp.variables['velocity_center_classes']
    netCDF_var_velocity_data = netCDF_var_velocity[:].data
    assert len(netCDF_var_velocity_data) == rootgrp.dimensions['velocity_classes'].size
    netCDF_var_diameter = rootgrp.variables['diameter_center_classes']
    netCDF_var_diameter_data = netCDF_var_diameter[:].data
    assert len(netCDF_var_diameter_data) == rootgrp.dimensions['diameter_classes'].size
    # test global attributes
    assert rootgrp.title == config_dict['global_attrs']['title']
    assert rootgrp.contributors == config_dict['global_attrs']['contributors']    
    pprint(rootgrp.__dict__)
    rootgrp.close()



def test_append_data_netCDF():
    # -- append data: test time
    amount_data_points = 10
    now = NowTime()
    fn_start = 'classtest'
    # write data
    for i in range(amount_data_points):
        new_time = now.utc + (i*timedelta(minutes=1)) # time offset: by 1 minute
        telegram = Telegram(config_dict=config_dict,
                    telegram_lines=parsivel_lines, 
                    timestamp=new_time, 
                    data_dir=test_data_dir,
                    data_fn_start=fn_start,
                    logger=logger)
        telegram.capture_prefixes_and_data()
        telegram.append_data_to_netCDF()

    # read and test
    rootgrp = Dataset(f'{test_data_dir/fn_start}.nc', 'r', format="NETCDF4")  # read netcdf
    netCDF_var_time = rootgrp.variables['time']
    netCDF_var_time_data = netCDF_var_time[:].data
    assert len(netCDF_var_time_data) == amount_data_points
    first_time_item = num2date(netCDF_var_time_data[0], units=f'hours since {now.utc.strftime("%Y-%m-%d")} 00:00:00 +00:00')
    assert first_time_item.strftime("%Y-%m-%mT%H:%M:%S") == now.utc.strftime("%Y-%m-%mT%H:%M:%S")

    netCDF_var_MOR = rootgrp.variables['MOR']
    netCDF_var_MOR_data = netCDF_var_MOR[:].data
    assert netCDF_var_MOR_data[0] == float(20000.0)
    netCDF_var_amp = rootgrp.variables['amplitude']
    netCDF_var_amp_data = netCDF_var_amp[:].data
    assert netCDF_var_amp_data[0] == 13894
    netCDF_var_temp_l_sensor = rootgrp.variables['T_L_sensor_head']
    netCDF_var_temp_l_sensor_data = netCDF_var_temp_l_sensor[:].data
    netCDF_var_temp_r_sensor = rootgrp.variables['T_R_sensor_head']
    netCDF_var_temp_r_sensor_data = netCDF_var_temp_r_sensor[:].data
    assert netCDF_var_temp_r_sensor_data[0] == netCDF_var_temp_l_sensor_data[0] # same temp on L & R sensors: only valid for current data

    # F93: data_raw - test shape is 32x32 ndarry for each data point
    netCDF_var_data_raw = rootgrp.variables['data_raw']
    netCDF_var_data_raw_data = netCDF_var_data_raw[:].data
    netCDF_var_data_raw_shape = netCDF_var_data_raw_data.shape
    print(netCDF_var_data_raw_shape)
    assert netCDF_var_data_raw_shape == (amount_data_points, 32, 32)
'''    
    # TODO: F61
    # # all_particles (f61)
    # netCDF_var_all_particles = rootgrp.variables['all_particles']
    # netCDF_var_all_particles_data = netCDF_var_all_particles[:].data
    # netCDF_var_all_particles_shape = netCDF_var_all_particles_data.shape  
    # # testing shape: should always be (number of data points, number of particles, 2) 
    # assert netCDF_var_all_particles_shape == (amount_data_points, len(telegram.f61_rows), 2)
    # # getting all_particles val from netCDF and telegram.f61_rows, rounding them to 4 decimal places and testing ==
    # sample_f61_vals = [round(float(i),4) for i in telegram.f61_rows[0]]
    # sample_netCDF_all_particles = netCDF_var_all_particles_data[0][0].tolist()
    # sample_netCDF_all_particles = [round(i,4) for i in sample_netCDF_all_particles]
    # assert sample_f61_vals == sample_netCDF_all_particles
'''

def create_test_data_dir(dir):
    if not os.path.exists(path=dir):
        os.mkdir(path=dir)

def delete_netcdf(fn_start, data_dir):
    test_nc_path = data_dir / f'{fn_start}.nc'
    if os.path.exists(test_nc_path):
        os.remove(test_nc_path)
