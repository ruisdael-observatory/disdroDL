from pathlib import Path 
import os
import subprocess

nc_path = Path(__file__).parent.parent / 'test_data' / '20230827_Lutjewad_Atmospheric_Station-LUTJEWAD_PAR009.nc' 
nc_path_tmp = Path(__file__).parent.parent / 'test_data' / nc_path.name.replace('.nc', '.nc.tmp')
print(nc_path, nc_path_tmp)
# invoke: nccopy -d6 /absolut/filepath
subprocess.run(['nccopy', '-d6', nc_path, nc_path_tmp  ])
# remove nc_path
os.remove(nc_path)
assert os.path.isfile(nc_path) == False

# move to nc_path_tmp to 
os.rename(nc_path_tmp, nc_path)
assert os.path.isfile(nc_path) == True
assert os.path.isfile(nc_path_tmp) == False


# before: 2.7M  20230827_Lutjewad_Atmospheric_Station-LUTJEWAD_PAR009.nc
# after: 594K  20230827_Lutjewad_Atmospheric_Station-LUTJEWAD_PAR009.nc
# test_data/20230827_Lutjewad_Atmospheric_Station-LUTJEWAD_PAR009.nc
