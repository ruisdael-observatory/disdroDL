"""
Manual polling of telegrams for Thies sensors
"""
from time import sleep
from pathlib import Path

from modules.sensors import Thies # pylint: disable=import-error
from modules.sqldb import create_db, connect_db # pylint: disable=import-error
from modules.util_functions import yaml2dict, create_logger # pylint: disable=import-error
from modules.now_time import NowTime # pylint: disable=import-error

if __name__ == '__main__':

    # -- Config files --
    wd = Path(__file__).parent
    config_dict = yaml2dict(path=wd / 'configs_netcdf' / 'config_006_GV_THIES.yml')

    # -- DB --
    db_path = Path(config_dict['data_dir']) / 'disdrodl-thies.db'
    create_db(dbpath=str(db_path))

    # -- Serial connection --
    thies_port = '/dev/ttyACM0'
    thies_baud = 9600
    thies_id = '06'
    thies = Thies(thies_id=thies_id)

    logger = create_logger(log_dir=Path(config_dict['log_dir']),
                           script_name=config_dict['script_name'],
                           sensor_name=config_dict['global_attrs']['sensor_name'])
    thies.init_serial_connection(thies_port, thies_baud, logger)
    thies.sensor_start_sequence(config_dict=config_dict, logger=logger)

    while True:
        now_time = NowTime()

        if int(now_time.time_list[2]) != 0:
            print(now_time.time_list)
            sleep(1)
            continue

        con, cur = connect_db(dbpath=str(db_path))

        output = thies.read(logger)

        insert = 'INSERT INTO disdrodl(timestamp, datetime, parsivel_id, telegram) VALUES'

        timestamp_str = now_time.utc.isoformat()
        ts = now_time.utc.timestamp()
        sensor = config_dict['global_attrs']['sensor_name']

        # Insert telegram into db
        insert_str = f"{insert} ({ts}, '{timestamp_str}', '{sensor}', '{output}');"

        cur.execute(insert_str)

        con.commit()
        cur.close()
        con.close()

        print(output)
        sleep(2)
