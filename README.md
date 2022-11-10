# Parsivel disdrometer data logger - version 2

**Data Aquisition Script for Parsifel Disdrometer**

(based on sftp.tudelft.nl:/staff-umbrella/Parsivel/Scripts/Parsivel_serial_communication_v3.py)

* Main script: [capture_disdrometer_data.py](capture_disdrometer_data.py)
* Configuration values: [config.yml](config.yml)
* Variables with Parsivel serial commands [parsivel_cmds.py](parsivel_cmds.py)
* Parsivel reset script: [reset_parsivel.py](reset_parsivel.py)
* Parsivel's set user defined telegram script: [request_telegram.py](request_telegram.py) 


TODO: script description
* setups parsival's to return user defined telegram 
    * requests parsivel to send user defined telegram
    * defines list of fields in  user defined telegram



TODO: install dependencies / run

Run:
`python capture_disdrometer_data.py`

# Changes implemented
- [X] variables in yaml file [config.yml](config.yml)
- [x] reset commands in another script [reset-parsivel.py](reset-parsivel.py)
- [X] time in UTC
- [X] include a logger
- [x] write to data dir
- [X] time.time() Not needed, remove
- [X] date format: isoformat() utcnow.
- [X] CSV sctructure: timestamp; telegram; or timestamp;field1;field2;... ?
- [ ] field 61 process parsivel_bytes to str and remove non-printing chars
- [ ] log and data dirs defined in config.yml
- [ ] add script user to dialout group (to access /dev/ttyUSB0)
- [X] service file
    - [ ] python executable path
    - [ ] script path
- [ ] python environment + requirements 
- [ ] Make file that:
        - [ ] stops and remove service (if present)
        - [ ] resets parsivel
        - [ ] creates and starts service

- [X] get full telegram an not only OTT(default telegram)
    - [X] check config
    - [X] change config with to User telegram mode = 1 with `'CS/M/M/1\r'.encode('utf-8')`
    - [X] check order of the telegram
- [ ] perform changes in reset_parsivel or at start of script
- [ ] output telegram in different columns (bytes -> str)
- [ ] include field numbers/name in csv header
- [ ] test receiving F61 with .readlines()  

