# Parsivel disdrometer data logger - version 2

**Data Logging Script for OTT Parsivel2 Disdrometer** Produces daily netCDF

* Main script: [capture_disdrometer_data.py](capture_disdrometer_data.py)
* Configuration files: 
    * general: [config_general.yml](config_general.yml) - *should not need editing*
    * parsivel specific: ie. [config_008_GV.yml](config_008_GV.yml) - **create 1 per parsivel**
* Parsivel reset script: [reset_parsivel.py](reset_parsivel.py)



## Operational Principals

**[capture_disdrometer_data.py](capture_disdrometer_data.py)**
* creates the data and log directories 
* sets up the serial communication with Parsivel 
* in while loop (every minute):
    * requests user defined telegram to OTT Parsivel
    * stores received telegram, processed and written to CSV files, though `class Telegram` defined in [modules/classes.py](modules/classes.py)

**Auxiliary functions** can are defined in [modules/util_functions.py](modules/util_functions.py)

**Time is set to UTC** 

**Data directories' structure:**
* parent data directory is defined in [config.yml](config.yml) `data_dir` 
* monthly data directories, inside parent data directory 
   * monthly data directories naming: `yyyymm`
* every day new data files created:
    * data files naming: `yyyymmdd_{site_name}_{station_code}_{sensor_name}_{fields}`

**Telegram field names and units**
In accordance to [OTT Parsivel2 official documentation](https://www.ott.com/download/operating-instructions-present-weather-sensor-ott-parsivel2-with-screen-heating-1/) the telegram field names and units are defined in [config.yml](config.yml) `telegram_fields` 


## Requirements

create and activate a python virtual environment

install python dependencies: `pip -r requirements.txt`

create log directory with read and write permissions to all users: `sudo mkdir /var/log/disdroDL/; sudo chmod a+rw /var/log/disdroDL` 

create data directory with read and write permissions to all users: `sudo mkdir /data/disdroDL/; sudo chmod a+rw /data/disdroDL` 

run Parsivel [reset script](./reset_parsivel.py): `python reset_parsivel.py`

create a station-spefic file and commit it to this repo (see [config_008_GV.yml](./config_008_GV.yml) as an example) 


## Run script

**manually**: 
* [capture_disdrometer_data.py](./capture_disdrometer_data.py) manually: `python capture_disdrometer_data.py -c config_NNN_??.yml `

**via service file**: 
* edit the config file name in [disdrodlv2.service](disdrodlv2.service) to match that of the station
* run: `systemctl enable disdrodlv2.service`
* run: `systemctl start disdrodlv2.service`
* check status: `systemctl status disdrodlv2.service`


## Outputs
**[capture_disdrometer_data.py](capture_disdrometer_data.py) outputs 4 CSV**
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
