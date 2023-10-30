# Parsivel disdrometer data logger - version 2

**Data Logging Script for OTT Parsivel2 Disdrometer** Produces daily netCDF

* Main script: [main.py](main.py)
* Configuration files: 
    * general: [configs_netcdf/config_general.yml](configs_netcdf/config_general.yml) - *should not need editing*
    * parsivel specific: ie. [configs_netcdf/config_008_GV.yml](configs_netcdf/config_008_GV.yml) - **create 1 per parsivel**
* Parsivel reset script: [reset_parsivel.py](reset_parsivel.py)



## Operational Principals

**[main.py](main.py)**
* reads configurations from [configs_netcdf/config_general.yml](configs_netcdf/config_general.yml) and target-device config
* creates the data and log directories 
* sets up the serial communication with Parsivel 
* in while loop (every minute):
    * requests user defined telegram to OTT Parsivel
    * stores received telegram, processed and written to netCDF file, though `class Telegram` defined in [modules/classes.py](modules/classes.py)

**Auxiliary functions** can are defined in [modules/util_functions.py](modules/util_functions.py)

**Time is set to UTC** 

**Data directories' structure:**
* parent data directory is defined in [configs_netcdf/config.yml](configs_netcdf/config.yml) `data_dir` 
* monthly data directories, inside parent data directory 
   * monthly data directories naming: `yyyymm`
* every day new data files created:
    * data files naming: `yyyymmdd_{site_name}_{station_code}_{sensor_name}_{fields}`

**Telegram field names and units**
In accordance to [OTT Parsivel2 official documentation](https://www.ott.com/download/operating-instructions-present-weather-sensor-ott-parsivel2-with-screen-heating-1/) the telegram field names and units are defined in [configs_netcdf/config.yml](configs_netcdf/config.yml) `telegram_fields` 


## Requirements

create and activate a python virtual environment and:
* install python dependencies: `pip -r requirements.txt`
* create log directory with read and write permissions to all users: `sudo mkdir /var/log/disdroDL/; sudo chmod a+rw /var/log/disdroDL` 
* create data directory with read and write permissions to all users: `sudo mkdir /data/disdroDL/; sudo chmod a+rw /data/disdroDL` 
* run Parsivel [reset script](./reset_parsivel.py): `python reset_parsivel.py`
* create a station-specific file and commit it to this repo (see [configs_netcdf/config_008_GV.yml](./configs_netcdf/config_008_GV.yml) as an example) 

Install netcdf-bin: `sudo apt install netcdf-bin`, to be able to compress netCDFs with `nccopy -d6` in `Telegram.compress_netcdf()` method.

## Run script

**As Linux Systemd Service**: 
* edit the config file name in [disdrodlv2.service](disdrodlv2.service) to match that of the station
* create system link between local service file and service files location: `ln disdrodlv2.service /etc/systemd/system/disdrodlv2.service`
* run: `systemctl enable disdrodlv2.service`
* run: `systemctl start disdrodlv2.service`
* check status: `systemctl status disdrodlv2.service`

**manually**: 
* [main.py](./main.py) manually: `python main.py -c configs_netcdf/config_NNN_??.yml `


## Outputs
**[main.py](main.py) outputs 4 CSV**
* `*_SVFS.csv` stores all single value fields (SVFS). Example: [sample_data/20230221_Delft-GV_PAR008_SVFS.csv](sample_data/20230221_Delft-GV_PAR008_SVFS.csv)
* `*_F61.csv` stores field 61 values (list of all particles detected between requests, including particle-size and speed ). Example: [sample_data/20230225_Delft-GV_PAR008_F61.csv](sample_data/20230225_Delft-GV_PAR008_F61.csv)
* `*_F90.csv` stores field 90 values (Field N). Example: [sample_data/20230225_Delft-GV_PAR008_F90.csv](sample_data/20230225_Delft-GV_PAR008_F90.csv)
* `*_F91.csv` stores field 91 values (Field v). Example: [sample_data/20230225_Delft-GV_PAR008_F91.csv](sample_data/20230225_Delft-GV_PAR008_F91.csv)
* `*_F93.csv` stores field 93 values (Raw data). Example: [sample_data/20230225_Delft-GV_PAR008_F93.csv](sample_data/20230225_Delft-GV_PAR008_F93.csv)


## Tests
* [test_functions.py](test_functions.py)
* [test_classes.py](test_classes.py)

run: `pytest -s`



## Debug Serial communication

with 2 different screens (use tmux multiplexer or 2 different shells)

terminal one: listen to serial port `tail -f /dev/ttyUSB0`

terminal two: send commands to serial port `echo -en "CS/L\r" > /dev/ttyUSB0`
