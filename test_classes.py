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

log_handler = StreamHandler()
logger = logging.getLogger('testlog')
logger.addHandler(log_handler)
wd = Path(__file__).parent 
test_data_dir = wd / 'test_data'
config_dict = yaml2dict(path = wd / 'config.yml')
prefixes_list = ['SVFS', 'F61', 'F90', 'F91', 'F93']
telegram_lines=[b'OK\r\n', 
                b'\n',
                b'SVFS:0000.432;0002.98;61;61;  -RA;  R-;18.865;16306;00060;12657;00137;006;2.00;24.2;0;0002.98;000;020;010;010;0002.05;0000.00;00000139;\n',
                b'F90:-9.999;-9.999;-9.999;02.608;02.642;02.520;02.366;02.070;02.051;01.773;00.818;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n',
                b'F91:00.000;00.000;00.000;01.716;01.723;01.862;02.534;03.280;03.228;03.000;03.900;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;00.000;\n',
                b'F93:000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;005;002;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;006;003;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;002;004;002;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;005;002;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;005;004;010;002;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;006;003;007;003;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;001;000;013;004;005;002;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;002;000;003;002;001;003;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;005;006;002;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;003;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;001;002;000;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;\n',
                b'F61:00.778;02.553\r\n', b'00.457;05.252\r\n', b'00.915;03.939\r\n', b'01.026;03.471\r\n', b'00.821;03.498\r\n', b'00.435;00.831\r\n', b'00.803;02.718\r\n', b'00.518;01.812\r\n', b'00.515;01.405\r\n', b'00.518;01.353\r\n', b'00.556;02.056\r\n', b'00.895;03.261\r\n', b'00.843;02.496\r\n', b'00.540;01.572\r\n', b'00.556;01.635\r\n', b'01.257;03.584\r\n', b'00.682;01.818\r\n', b'00.460;01.905\r\n', b'00.570;01.721\r\n', b'00.666;01.898\r\n', b'00.849;02.514\r\n', b'00.712;02.349\r\n', b'00.768;02.603\r\n', b'01.131;03.140\r\n', b'00.596;01.754\r\n', b'01.134;03.152\r\n', b'00.431;02.278\r\n', b'00.604;01.825\r\n', b'00.390;01.033\r\n', b'00.415;01.478\r\n', b'00.885;04.175\r\n', b'00.471;01.040\r\n', b'00.471;02.202\r\n', b'00.464;01.804\r\n', b'00.509;01.502\r\n', b'00.478;02.401\r\n', b'00.411;01.472\r\n', b'00.606;01.920\r\n', b'01.008;02.815\r\n', b'00.707;02.052\r\n', b'00.568;00.910\r\n', b'00.540;01.041\r\n', b'01.100;02.786\r\n', b'01.104;02.664\r\n', b'00.575;01.284\r\n', b'00.478;01.056\r\n', b'00.856;02.042\r\n', b'00.792;02.586\r\n', b'00.634;01.867\r\n', b'00.898;03.720\r\n', b'00.481;02.200\r\n', b'01.471;04.650\r\n', b'00.824;02.724\r\n', b'00.681;01.387\r\n', b'00.790;02.618\r\n', b'00.675;01.866\r\n', b'00.604;01.811\r\n', b'00.929;03.383\r\n', b'00.423;01.680\r\n', b'00.983;02.753\r\n', b'00.963;02.684\r\n', b'00.710;02.088\r\n', b'00.540;01.303\r\n', b'00.690;01.870\r\n', b'00.386;04.068\r\n', b'00.968;03.956\r\n', b'00.825;02.696\r\n', b'00.615;02.879\r\n', b'01.017;04.179\r\n', b'00.423;02.343\r\n', b'00.627;02.365\r\n', b'00.953;02.624\r\n', b'00.931;03.369\r\n', b'00.453;02.159\r\n', b'00.486;01.807\r\n', b'00.407;01.976\r\n', b'00.460;02.159\r\n', b'01.080;03.214\r\n', b'01.022;02.671\r\n', b'00.846;02.147\r\n', b'00.553;01.250\r\n', b'00.672;01.437\r\n', b'01.106;03.342\r\n', b'00.730;01.209\r\n', b'00.652;01.204\r\n', b'00.737;01.807\r\n', b'00.703;01.451\r\n', b'01.157;02.773\r\n', b'00.904;03.375\r\n', b'00.876;03.315\r\n', b'01.115;04.152\r\n', b'00.492;00.542\r\n', b'00.521;02.182\r\n', b'00.867;03.163\r\n', b'00.620;02.401\r\n', b'01.098;03.468\r\n', b'01.136;02.736\r\n', b'00.853;02.762\r\n', b'00.659;01.763\r\n', b'01.003;03.544\r\n', b'00.746;01.896\r\n', b'00.799;01.794\r\n', b'00.772;01.996\r\n', b'01.158;03.385\r\n', b'00.558;01.626\r\n', b'01.160;02.965\r\n', b'01.089;03.509\r\n', b'00.728;02.396\r\n', b'00.813;02.774\r\n', b'00.858;03.052\r\n', b'01.135;03.513\r\n', b'00.989;03.051\r\n', b'00.584;01.180\r\n', b'00.641;02.159\r\n', b'00.561;02.327\r\n', b'00.756;02.809\r\n', b'00.717;01.805\r\n', b'00.819;02.090\r\n', b'00.749;01.931\r\n', b'00.805;01.979\r\n', b'00.460;01.069\r\n', b'00.501;03.035\r\n', b'00.481;01.264\r\n', b'00.534;01.726\r\n', b'00.756;02.627\r\n', b'00.610;01.486\r\n', b'00.394;01.833\r\n', b'00.718;01.839\r\n', b'00.802;02.723\r\n', b'00.925;02.597\r\n', b'01.046;02.600\r\n', b'00.414;01.034\r\n', b'00.631;02.206\r\n', b'00.390;03.155\r\n', b'00.896;03.095\r\n', b'00.598;01.226\r\n', b'01.081;02.742\r\n', b'00.707;01.628\r\n', b'00.506;01.286\r\n', b';'
                ]

svfs = '%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%16;%17;%18;%24;%25;%26;%27;%28;%34;%35;%60;'

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


          


def test_Telegram_netCDF():
    now = NowTime()
    now.date_strings()
    fn_start = 'classtest'
    create_test_data_dir(dir=test_data_dir)
    delete_netcdf(fn_start='classtest', data_dir=test_data_dir,)  # delete old netCDF
    telegram = Telegram(config_dict=config_dict,
                        telegram_lines=telegram_lines, 
                        timestamp=now.utc, 
                        data_dir=test_data_dir,
                        data_fn_start=fn_start,
                        logger=logger)     
    
    telegram.create_netCDF() # in production code: runs if f'{fn_start}.nc' is not present
    # test dimensions
    rootgrp = Dataset(f'{test_data_dir/fn_start}.nc', 'r', format="NETCDF4")  # read netcdf
    assert set(['time', 'diameter_classes', 'velocity_classes']).issubset(set(rootgrp.dimensions.keys()))
    netCDF_var_velocity = rootgrp.variables['velocity_classes']
    netCDF_var_velocity_data = netCDF_var_velocity[:].data
    assert len(netCDF_var_velocity_data) == rootgrp.dimensions['velocity_classes'].size
    netCDF_var_diameter = rootgrp.variables['diameter_classes']
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
    now.date_strings()
    fn_start = 'classtest'
    # write data
    for i in range(amount_data_points):
        new_time = now.utc + (i*timedelta(minutes=1)) # time offset: by 1 minute
        telegram = Telegram(config_dict=config_dict,
                    telegram_lines=telegram_lines, 
                    timestamp=new_time, 
                    data_dir=test_data_dir,
                    data_fn_start=fn_start,
                    logger=logger)  
        telegram.capture_prefixes_and_data()
        telegram.append_data_to_netCDF() # here we are appending 
    # read and test
    rootgrp = Dataset(f'{test_data_dir/fn_start}.nc', 'r', format="NETCDF4")  # read netcdf
    netCDF_var_time = rootgrp.variables['time']
    netCDF_var_time_data = netCDF_var_time[:].data
    assert len(netCDF_var_time_data) == amount_data_points
    first_time_item = num2date(netCDF_var_time_data[0], units=f'hours since {now.utc.strftime("%Y-%m-%d")} 00:00:00 +00:00')
    assert first_time_item == now.utc
    last_time_item = num2date(netCDF_var_time_data[-1], units=f'hours since {now.utc.strftime("%Y-%m-%d")} 00:00:00 +00:00')
    elapsed_time = last_time_item - first_time_item
    elapsed_time_secs = elapsed_time.total_seconds() / 60
    assert elapsed_time_secs == (amount_data_points - 1)
    print('elapsed_time_secs:', elapsed_time_secs)

    netCDF_var_timestamp = rootgrp.variables['timestamp']
    assert netCDF_var_timestamp[0] == first_time_item.isoformat() and netCDF_var_timestamp[-1] == last_time_item.isoformat()

    netCDF_var_MOR = rootgrp.variables['MOR']
    netCDF_var_MOR_data = netCDF_var_MOR[:].data
    assert netCDF_var_MOR_data[0] == float(16306.0)
    netCDF_var_amp = rootgrp.variables['amplitude']
    netCDF_var_amp_data = netCDF_var_amp[:].data
    assert netCDF_var_amp_data[0] == 12657

    netCDF_var_temp_l_sensor = rootgrp.variables['T_L_sensor_head']
    netCDF_var_temp_l_sensor_data = netCDF_var_temp_l_sensor[:].data
    netCDF_var_temp_r_sensor = rootgrp.variables['T_R_sensor_head']
    netCDF_var_temp_r_sensor_data = netCDF_var_temp_r_sensor[:].data
    assert netCDF_var_temp_r_sensor_data[0] == netCDF_var_temp_l_sensor_data[0] # same temp on L & R sensors: only valid for current data

    # data_raw shape is 32x32 ndarry for each data point
    netCDF_var_data_raw = rootgrp.variables['data_raw']
    netCDF_var_data_raw_data = netCDF_var_data_raw[:].data
    netCDF_var_data_raw_shape = netCDF_var_data_raw_data.shape
    assert netCDF_var_data_raw_shape == (amount_data_points, 32, 32)

    # all_particles (f61)
    netCDF_var_all_particles = rootgrp.variables['all_particles']
    netCDF_var_all_particles_data = netCDF_var_all_particles[:].data
    netCDF_var_all_particles_shape = netCDF_var_all_particles_data.shape  
    # testing shape: should always be (number of data points, number of particles, 2) 
    assert netCDF_var_all_particles_shape == (amount_data_points, len(telegram.f61_rows), 2)
    # getting all_particles val from netCDF and telegram.f61_rows, rounding them to 4 decimal places and testing ==
    sample_f61_vals = [round(float(i),4) for i in telegram.f61_rows[0]]
    sample_netCDF_all_particles = netCDF_var_all_particles_data[0][0].tolist()
    sample_netCDF_all_particles = [round(i,4) for i in sample_netCDF_all_particles]
    assert sample_f61_vals == sample_netCDF_all_particles


def create_test_data_dir(dir):
    if not os.path.exists(path=dir):
        os.mkdir(path=dir)

def delete_csv(fn_start, prefix, data_dir):
    test_csv_path = data_dir / f'{fn_start}_{prefix}.csv'
    if os.path.exists(test_csv_path):
        os.remove(test_csv_path)

def delete_netcdf(fn_start, data_dir):
    test_nc_path = data_dir / f'{fn_start}.nc'
    if os.path.exists(test_nc_path):
        os.remove(test_nc_path)
