import sys
from argparse import ArgumentParser
from pathlib import Path

from modules.sqldb import connect_db
from modules.util_functions import yaml2dict


def column_exists(cur, column_name):
    cur.execute("PRAGMA table_info(disdrodl)")
    columns = cur.fetchall()
    for column in columns:
        if column[1] == column_name:
            return True
    return False


def main(config_site):
    wd = Path(__file__).parent

    config_dict_site = yaml2dict(path=wd / config_site)

    db_path = Path(config_dict_site['data_dir']) / 'disdrodl.db'

    con, cur = connect_db(dbpath=str(db_path))

    query = """
        ALTER TABLE disdrodl
        RENAME COLUMN parsivel_id TO sensor_id
    """

    exists = column_exists(cur, 'parsivel_id')
    if not exists:
        cur.close()
        con.close()
        sys.exit(0)

    cur.execute(query)
    con.commit()
    cur.close()
    con.close()


def get_config_file():
    """
    Function that gets th config file from the command line
    :return: the config file's name
    """
    parser = ArgumentParser(
        description="Upgrade the disdrodl.db database to change the column name from 'parsivel_id' to 'sensor_id")
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='Path to site config file. ie. -c configs_netcdf/config_008_GV.yml')
    args = parser.parse_args()
    return args.config


if __name__ == '__main__':
    main(get_config_file())
