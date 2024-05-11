from time import sleep
from pathlib import Path
import serial

from modules.sqldb import create_db, connect_db
from modules.util_functions import yaml2dict
from modules.now_time import NowTime

if __name__ == '__main__':
    
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_008_GV_THIES.yml')

    db_path = Path(config_dict['data_dir']) / 'disdrodl-thies.db'
    create_db(dbpath=str(db_path))

    thies_port = '/dev/ttyACM0'
    thies_baud = 9600
    thies_id = '06'
    thies = serial.Serial(port=thies_port, baudrate=thies_baud, timeout=10)
    thies.reset_input_buffer()
    thies.reset_output_buffer()
    print(thies)

    thies.write(('\r' + thies_id + 'KY00001\r').encode('utf-8')) # place in config mode
    sleep(1)

    # thies.write(('\r' + thies_id + 'RS00001\r').encode('utf-8')) # restart sensor
    # print("restarting")
    # sleep(20)
    #
    # thies.write(('\r' + thies_id + 'KY00001\r').encode('utf-8')) # place in config mode
    # sleep(1)

    thies.write(('\r' + thies_id + 'TM00000\r').encode('utf-8')) # turn of automatic mode
    sleep(1)

    thies.write(('\r' + thies_id + 'ZH000' + NowTime().time_list[0] + '\r').encode('utf-8')) # set hour
    sleep(1)

    thies.write(('\r' + thies_id + 'ZM000' + NowTime().time_list[1] + '\r').encode('utf-8')) # set minutes
    sleep(1)

    thies.write(('\r' + thies_id + 'ZS000' + NowTime().time_list[2] + '\r').encode('utf-8')) # set seconds
    sleep(1)

    thies.write(('\r' + thies_id + 'KY00000\r').encode('utf-8')) # place out of config mode
    sleep(1)

    while True:
        now_time = NowTime()

        if int(now_time.time_list[2]) != 0:
            print(now_time.time_list)
            sleep(1)
            continue

        con, cur = connect_db(dbpath=str(db_path))

        thies.write(('\r' + thies_id + 'TR00005\r').encode('utf-8'))
        output = thies.readline()
        decoded_bytes = str(output[0:len(output)-2].decode("utf-8"))

        insert = 'INSERT INTO disdrodl(timestamp, datetime, parsivel_id, telegram) VALUES'

        timestamp_str = now_time.utc.isoformat()
        ts = now_time.utc.timestamp()
        sensor = config_dict['global_attrs']['sensor_name']

        insert_str = f"{insert} ({ts}, '{timestamp_str}', '{sensor}', '{decoded_bytes}');"

        cur.execute(insert_str)

        con.commit()
        cur.close()
        con.close()

        print(decoded_bytes)
        sleep(2)
