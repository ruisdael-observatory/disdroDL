# Parsivel disdrometer data logger - version 2

**Data Aquisition Script for Parsifel Disdrometer**

* Main script: [capture_disdrometer_data.py](capture_disdrometer_data.py)
* Configuration values: [config.yml](config.yml)
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

create symbolic link between the station's config file and config.yml
`ln config_GV_008.yml config.yml`


## Run script

**manually**: 
* [capture_disdrometer_data.py](./capture_disdrometer_data.py) manually: `python capture_disdrometer_data.py`

**via service file**: 
* [disdrodlv2.service](disdrodlv2.service)


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


# TODO
- [X] NetCDF global attributes - same as ACTRIS
- [ ] handling time dimension ??
- [ ] Xarray: could it makes it easier? https://xarray.pydata.org/en/v0.13.0/why-xarray.html
- [ ] turn telegram_fields to netCDF vars
- [ ] config.yml: possible split in 2: constant values, over written by site specific values file: `config.yml` & `site.yml`