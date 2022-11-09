# Parsivel disdrometer data logger - version 2

**Data Aquisition Script for Parsifel Disdrometer**

(based on sftp.tudelft.nl:/staff-umbrella/Parsivel/Scripts/Parsivel_serial_communication_v3.py)

* Main script: [capture_disdrometer_data.py](capture_disdrometer_data.py)
* Configuration values: [config.yml](config.yml)
* Parsivel reset script: [reset_parsivel.py](reset_parsivel.py)


TODO: script description

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
- [ ] service file
- [ ] Make file that:
        - [ ] stops and remove service (if present)
        - [ ] resets parsivel
        - [ ] creates and starts service