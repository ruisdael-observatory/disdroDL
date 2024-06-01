"""
This file contains the tests for the main.py file.

The main goal of this file is to test the main loop of the program,
which logs data once every minute.
"""
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from main import main
from modules.sensors import Thies
from modules.sqldb import connect_db

wd = Path(__file__).parent


class TestThiesIntegration(unittest.TestCase):
    """
    Class for testing main.py for the Thies sensor.

    Functions:
    - test_bad_sensor_type: Test for a bad sensor type, and if the logger writes the correct thing to file.
    - test_main_loop: Test for the main loop of the Thies sensor.
    """
    thies_line = ('06;0854;2.11;01.01.14;18:59:00;00;00;NP   ;000.000;00;00;NP   '
                  ';000.000;000.000;000.000;0000.00;99999;-9.9;100;0.0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;+23;26;1662'
                  ';4011;2886;258;062;063;+20.3;999;9999;9999;9999;00000;00000.000;00000;00000.000;00000;00000.000'
                  ';00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000'
                  ';00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                  ';000;000;000;000;000;000;000;000;99999;99999;9999;999;E9;')

    @patch('main.sys')
    @patch('main.yaml2dict')
    @patch('main.create_logger')
    def test_bad_sensor_type(self, mock_create_logger, mock_yaml2dict, mock_sys):
        """
        Test for a bad sensor type, and if the logger writes the correct thing to file
        :param mock_create_logger: the mocked logger
        :param mock_yaml2dict: mock yaml2dict
        :param mock_sys: mock sys object
        """
        test_conf_dict_site = {
            'log_dir': 'value1',
            'script_name': 'value2',
            'global_attrs': {
                'sensor_name': 'sensor_name',
                'sensor_type': 'sensor_type',
            }

        }
        mock_logger = Mock()
        mock_create_logger.return_value = mock_logger

        mock_yaml2dict.return_value = test_conf_dict_site
        mock_sys.exit.side_effect = sys.exit
        with pytest.raises(SystemExit):
            main('config_008_GV.yml')

        mock_sys.exit.assert_called_once_with(1)
        mock_logger.error.assert_called_once_with(msg="Sensor type sensor_type not recognized")

    @patch('modules.sensors.sleep', return_value=None)
    @patch.object(Thies, 'read')
    @patch('main.NowTime')
    @patch('main.yaml2dict')
    @patch('main.sleep', return_value=None)
    @patch('modules.sensors.serial', )
    def test_main_loop(self, mock_serial, mock_sleep, mock_yaml2dict, # pylint: disable=unused-argument
                       mock_now_time, mock_read, mock_sensor_sleep): # pylint: disable=unused-argument
        """
        Test for the main loop of the Thies sensor, it checks whether there are 1440 rows in the database.
        :param mock_serial: mock serial object
        :param mock_sleep: mock sleep object to skip the sleep time
        :param mock_yaml2dict: mock yaml2dict object
        :param mock_now_time: mock NowTime object to always be on a whole minute
        :param mock_read: mock read object to return a Thies line
        :param mock_sensor_sleep: mock sensor sleep object to skip sleep in sensor class
        """

        mock_read.return_value = ('06;0854;2.11;04.01.14;09:52:01;00;00;NP   ;000.000;00;00;NP   '
                                  ';000.000;000.000;000.000;0006.96;99999;-9.9;100;0.0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0'
                                  ';0;+32;37;1774;4011;2756;276;028;037;+25.9;999;9999;9999;9999;00002;00000.000'
                                  ';00000;00000.000;00000;00000.000;00000;00000.000;00001;00000.007;00000;00000.000'
                                  ';00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000;00000;00000.000'
                                  ';00000;00000.000;00000;00000.000;00001;00000.009;00000;00000.000;000;000;000;000'
                                  ';000;000;000;000;000;000;001;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;001;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000'
                                  ';000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;000;99999;99999;9999'
                                  ';999;B1;')

        test_conf_dict_site = {
            'log_dir': 'sample_data',
            'data_dir': 'sample_data',
            'script_name': 'test_log',
            'port': '/dev/ttyACM0',
            'baud': 9600,
            'global_attrs': {
                'sensor_name': 'THIES006',
                'sensor_type': 'Thies Clima',
            }

        }

        mock_yaml2dict.return_value = test_conf_dict_site

        mock_now_time.return_value.time_list = ['10', '10', '00']
        mock_now_time.return_value.utc = datetime.now(timezone.utc)

        def side_effect(seconds): # pylint: disable=unused-argument
            if mock_sleep.call_count > 1440:
                raise KeyboardInterrupt

        mock_sleep.side_effect = side_effect

        with self.assertRaises(KeyboardInterrupt):
            main('configs_netcdf/config_008_GV_THIES.yml')

        con, cur = connect_db(dbpath='sample_data/disdrodl-test1.db')
        number_of_rows = len(con.execute('SELECT * FROM disdrodl').fetchall())
        assert number_of_rows == 1440
        cur.close()
        con.close()
        os.remove('sample_data/disdrodl-test1.db')
        os.remove('sample_data/log_test_log.json')
