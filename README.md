# Parsivel disdrometer data logger - version 2

**Data Aquisition Script for Parsifel Disdrometer**

* Main script: [capture_disdrometer_data.py](capture_disdrometer_data.py)
* Configuration values: [config.yml](config.yml)
* Parsivel reset script: [reset_parsivel.py](reset_parsivel.py)

## Outputs
[capture_disdrometer_data.py](capture_disdrometer_data.py) outputs 4 CSV to the data dir (see data_dir variable in [config_GV_008.yml](config_GV_008.yml) )

CSVS:
* `*_SVFS.csv` stores all single value fields (SVFS). Example: [sample_data/20230221_Delft-GV_PAR008_SVFS.csv](sample_data/20230221_Delft-GV_PAR008_SVFS.csv)
* `*_F61.csv` stores field 61 values (list of all particles detected between requests, including particle-size and speed ). Example: [sample_data/20230221_Delft-GV_PAR008_F61.csv](sample_data/20230221_Delft-GV_PAR008_F61.csv)
* `*_F90.csv` stores field 90 values (Field N). Example: [sample_data/20230221_Delft-GV_PAR008_F90.csv](sample_data/20230221_Delft-GV_PAR008_F90.csv)
* `*_F91.csv` stores field 91 values (Field v). Example: [sample_data/20230221_Delft-GV_PAR008_F91.csv](sample_data/20230221_Delft-GV_PAR008_F91.csv)
* `*_F93.csv` stores field 93 values (Raw data). Example: [sample_data/20230221_Delft-GV_PAR008_F93.csv](sample_data/20230221_Delft-GV_PAR008_F93.csv)




**[capture_disdrometer_data.py](capture_disdrometer_data.py) execusion steps**

**TODO: rewrite**

* creates the data and log directories 
* sets up the serial communication with Parsivel 
* sends the desired configuration (`parsivel_user_telegram` & `parsivel_set_telegram_list`) to Parsivel
* starts a endless loop, where:
    * time (in UTC) is checked: 
    * each new day a new data dir, data files and a log are created
    * Parsivel telegram is requested and processed:
        * telegrams with 1 line of length >= 20 are all fileds, except 61
            * they are written to data file with format YYYYMMdd_Parsivel_name.csv
            * request field 61
        * telegrams with more than 1 line, are fields 61, which includes a list of particle size & particle speed pairs 
            * they are written to data file: YYYYMMdd_Parsivel_name_field61.csv


TODO: script description
* setups parsival's to return user defined telegram 
    * requests parsivel to send user defined telegram
    * defines list of fields in  user defined telegram

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
* [disdrodlv2.service](disdrodlv2.service) **TODO**

## Debug Serial communcation

with 2 different screens (use tmux multiplexer or 2 different shells)

terminal one: listen to serial port `tail -f /dev/ttyUSB0`

terminal two: send commands to serial port `echo -en "CS/L\r" > /dev/ttyUSB0`

## Tests
in [test_functions.py](test_functions.py)

run: `pytest -s`


# Changes implemented
- [X] variables in yaml file [config.yml](config.yml)
- [x] reset commands in another script [reset-parsivel.py](reset-parsivel.py)
- [X] time in UTC
- [X] include a logger
- [x] write to data dir
- [X] time.time() Not needed, remove
- [X] date format: isoformat() utcnow.
- [X] CSV sctructure: timestamp; telegram; or timestamp;field1;field2;... ?
- [X] log and data dirs defined in config.yml
- [X] output telegram in different columns (bytes -> str)
- [X] include field numbers/name in csv header
- [X] get full telegram an not only OTT(default telegram)
    - [X] check config
    - [X] change config with to User telegram mode = 1 with `'CS/M/M/1\r'.encode('utf-8')`
    - [X] check order of the telegram
- [X] test receiving F61 with .readlines()  
- [ ] perform changes in reset_parsivel or at start of script
- [ ] add script user to dialout group (to access /dev/ttyUSB0)
- [ ] field 61 process parsivel_bytes to str and remove non-printing chars
- [X] service file
    - [ ] in documentation mention: python executable path
    - [ ] in documentation mention: script path
- [ ] Make file or Ansible playbook that:
        - [ ] stops and remove service (if present)
        - [ ] resets parsivel
        - [ ] creates and starts service


