from time import sleep
from pathlib import Path
import serial

from modules.sqldb import create_db, connect_db
from modules.util_functions import yaml2dict, thies_start_sequence
from modules.now_time import NowTime

if __name__ == '__main__':

    # -- Config files --
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV_THIES.yml')

    # -- DB --
    db_path = Path(config_dict['data_dir']) / 'disdrodl-thies.db'
    create_db(dbpath=str(db_path))

    # -- Serial connection --
    thies_port = '/dev/ttyACM0'
    thies_baud = 9600
    thies_id = '06'
    thies = serial.Serial(port=thies_port, baudrate=thies_baud, timeout=10)

    thies_start_sequence(thies, thies_id)

    while True:
        now_time = NowTime()

        if int(now_time.time_list[2]) != 0:
            print(now_time.time_list)
            sleep(1)
            continue

        con, cur = connect_db(dbpath=str(db_path))

        # Send request to get the latest telegram
        sleep(2) # Give sensor some time to create the telegram
        thies.write(('\r' + thies_id + 'TR00005\r').encode('utf-8'))
        output = thies.readline()
        decoded_bytes = str(output[0:len(output)-2].decode("utf-8"))

        insert = 'INSERT INTO disdrodl(timestamp, datetime, parsivel_id, telegram) VALUES'

        timestamp_str = now_time.utc.isoformat()
        ts = now_time.utc.timestamp()
        sensor = config_dict['global_attrs']['sensor_name']

        # Insert telegram into db
        insert_str = f"{insert} ({ts}, '{timestamp_str}', '{sensor}', '{decoded_bytes}');"

        cur.execute(insert_str)

        con.commit()
        cur.close()
        con.close()

        print(decoded_bytes)
        sleep(2)
