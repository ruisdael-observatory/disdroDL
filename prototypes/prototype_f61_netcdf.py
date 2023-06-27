from random import shuffle
import numpy
from netCDF4 import Dataset
from datetime import datetime, timedelta
from cftime import date2num 

# creating new file
netCDF_rootgrp = Dataset("test_data/f61_test.nc", "w", format="NETCDF4")
                         # global attributes
netCDF_rootgrp.description = "A test netDCDF for F61"
netCDF_rootgrp.date = datetime.utcnow().strftime("%Y.%m.%d") 

# dimensions to netCDF_rootgrp
time_d = netCDF_rootgrp.createDimension("time",None)
size_d = netCDF_rootgrp.createDimension("size",None)
speed_d = netCDF_rootgrp.createDimension("speed",None)

# variables
netCDF_var_time = netCDF_rootgrp.createVariable("time", "f8", ("time",))
netCDF_var_time.long_name = 'Time UTC'
netCDF_var_time.units = f'hours since {datetime.utcnow().strftime("%Y-%m-%d")} 00:00:00'
netCDF_var_time.standard_name = 'time'
netCDF_var_time.calendar = 'standard'
netCDF_var_time.axis = 'T'

# # NOTE: not using size and speed vars
# netCDF_var_f61_size = netCDF_rootgrp.createVariable("field61_size", "f8", ("size"))
# netCDF_var_f61_size.long_name = 'Field61 particle size'
# netCDF_var_f61_size.standard_name = 'field61_size'
# netCDF_var_f61_size.units = 'mm'

# netCDF_var_f61_speed = netCDF_rootgrp.createVariable("field61_speed", "f8", ("speed"))
# netCDF_var_f61_speed.long_name = 'Field61 particle speed'
# netCDF_var_f61_speed.standard_name = 'field61_speed'
# netCDF_var_f61_speed.units = 'm/s'

netCDF_var_f61_all_particles = netCDF_rootgrp.createVariable("all_particles", "f8", ("time","size", "speed"))
netCDF_var_f61_all_particles.long_name = 'List of all particles detected (particle-size speed)'
netCDF_var_f61_all_particles.standard_name = 'all_particles'


# data
masterlist = [['2023-04-04T10:47:10.167121', '00.502', '00.853'], ['2023-04-04T10:47:10.167121', '00.606', '02.026'], ['2023-04-04T10:47:10.167121', '00.550', '01.595'], ['2023-04-04T10:47:10.167121', '00.521', '01.237'], ['2023-04-04T10:47:10.167121', '00.540', '01.070']]

# 1st entry
now_time_obj = datetime.utcnow()
time_now_array = date2num([now_time_obj], units=netCDF_var_time.units,calendar=netCDF_var_time.calendar)
netCDF_var_time[:] = numpy.concatenate([netCDF_var_time[:].data, time_now_array])

data_list0 = masterlist
data_list0 = [i[1:] for i in data_list0] # remove timestamps
data_list0 = numpy.array(data_list0)
print(data_list0.shape)
netCDF_var_f61_all_particles[0] = data_list0

# 2n entry
now_time_obj = now_time_obj + timedelta(minutes=1)
time_now_array = date2num([now_time_obj], units=netCDF_var_time.units,calendar=netCDF_var_time.calendar)
netCDF_var_time[:] = numpy.concatenate([netCDF_var_time[:].data, time_now_array])

shuffle(masterlist) 
data_list1 = masterlist
data_list1 = [i[1:] for i in data_list1[2:]] # remove timestamps and only use elements from index 2 onward from masterlist
data_list1 = numpy.array(data_list1)
print(data_list1.shape)
netCDF_var_f61_all_particles[1] = data_list1

print('netCDF_var_f61_all_particles.shape:', netCDF_var_f61_all_particles.shape)

netCDF_rootgrp.close()

# output netcdf:
# ncdump test_data/f61_test.nc  
'''
netcdf f61_test {
dimensions:
        time = UNLIMITED ; // (2 currently)
        size = UNLIMITED ; // (5 currently)
        speed = UNLIMITED ; // (2 currently)
variables:
        double time(time) ;
                time:long_name = "Time UTC" ;
                time:units = "hours since 2023-04-04 00:00:00" ;
                time:standard_name = "time" ;
                time:calendar = "standard" ;
                time:axis = "T" ;
        double all_particles(time, size, speed) ;
                all_particles:long_name = "List of all particles detected (particle-size speed)" ;
                all_particles:standard_name = "all_particles" ;

// global attributes:
                :description = "A test netDCDF for F61" ;
                :date = "2023.04.04" ;
data:

 time = 14.6616741977778, 14.6783408644444 ;

 all_particles =
  {{0.502, 0.853},
  {0.606, 2.026},
  {0.55, 1.595},
  {0.521, 1.237},
  {0.54, 1.07}},
  {{0.606, 2.026},
  {0.502, 0.853},
  {0.521, 1.237},
  {_, _},
  {_, _}} ;
}

'''