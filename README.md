# Data Aquisition Script for Parsifel Disdrometer

based on sftp.tudelft.nl:/staff-umbrella/Parsivel/Scripts/Parsivel_serial_communication_v3.py

script: [capture_disdo_data.py](capture_disdo_data.py)

## changes
- [X] variables in yaml file [config.yml](config.yml)
    - [ ] variables with appended names and/or time need to be completed in py script
- [ ] reset commands in another script [reset-parsivel.py](reset-parsivel.py)
- [X] time in UTC
- [X] include a logger
- [ ] add script user to dialout group (to access /dev/ttyUSB0)
- [x] write to data dir
- [X] time.time() Not needed, remove
- [X] date format: isoformat() utcnow.
- [ ] field 61 process parsivel_bytes to str and remove non-printing chars
- [ ] log and data dirs defined in config.yml
- [X] CSV sctructure: timestamp; telegram; or timestamp;field1;field2;... ?


* varaibles are set 
    * Q: are they ever used? for setting up
    * change: set varaibles outside the script in yml
* serial communication is initiated
* while loop: reads serial communication output lines; line is appended to that days CSV
    * Change: there should be a sleep at while loop: it is in 69
    * Q: is time set in UTC? NO, local time. should be changed to UTC
    * Q: why is parsivel_request_field_61 sent to serial? (L55) because it needs a request to send the data back
    * Q: what version of python is used? think is version 2 as there is utf-8 encoding
* Change: logger should be used
'''