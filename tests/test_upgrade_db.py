import unittest
from unittest.mock import patch, Mock

import upgrade_db
from upgrade_db import get_config_file


class TestUpgradeDb(unittest.TestCase):

    @patch('upgrade_db.ArgumentParser')
    def test_get_config_file(self, mock_argument_parser):
        """
        Tests for the get_config_file function
        :param mock_argument_parser: Mock object for the ArgumentParser call
        """
        mock_parser = Mock()
        mock_argument_parser.return_value = mock_parser
        mock_args = Mock()
        mock_args.config = "config_PAR_008_GV.yml"
        mock_parser.parse_args.return_value = mock_args

        res = get_config_file()

        self.assertEqual(res, "config_PAR_008_GV.yml")
        mock_argument_parser.assert_called_once_with(
            description="Upgrade the disdrodl.db database to change the column name from 'parsivel_id' to 'sensor_id"
        )
        mock_parser.add_argument.assert_called_once_with('-c',
                                                         '--config',
                                                         required=True,
                                                         help='Path to site config file. ie. -c configs_netcdf/config_PAR_008_GV.yml')
        mock_parser.parse_args.assert_called_once()

    @patch('upgrade_db.connect_db')
    def test_column_exists_fail(self, mock_connect_db):
        mock_cur = Mock()
        mock_con = Mock()

        mock_connect_db.return_value = mock_con, mock_cur
        mock_cur.fetchall.return_value = [(0, 'test_column', 'TEXT', 0, None, 0)]
        result = upgrade_db.column_exists(mock_cur, 'parsivel_id')
        assert result is False

    @patch('upgrade_db.connect_db')
    def test_column_exists_success(self, mock_connect_db):
        mock_cur = Mock()
        mock_con = Mock()

        mock_connect_db.return_value = mock_con, mock_cur
        mock_cur.fetchall.return_value = [(0, 'parsivel_id', 'TEXT', 0, None, 0)]
        result = upgrade_db.column_exists(mock_cur, 'parsivel_id')
        assert result is True

    @patch('upgrade_db.column_exists', return_value=True)
    @patch('upgrade_db.connect_db')
    @patch('upgrade_db.yaml2dict')
    def test_main_success(self, mock_yaml2dict, mock_connect_db, mock_column_exists):  #pylint: disable=unused-argument
        mock_cur = Mock()
        mock_con = Mock()

        mock_connect_db.return_value = mock_con, mock_cur

        site_dict = {
            'data_dir': 'value1',
        }

        upgrade_db.main('config_PAR_008_GV.yml')
        mock_cur.execute.assert_called_once()
        mock_con.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_con.close.assert_called_once()

    @patch('upgrade_db.column_exists', return_value=False)
    @patch('upgrade_db.connect_db')
    @patch('upgrade_db.yaml2dict')
    def test_main_fail(self, mock_yaml2dict, mock_connect_db,
                       mock_column_exists):  #pylint: disable=unused-argument
        mock_cur = Mock()
        mock_con = Mock()

        mock_connect_db.return_value = mock_con, mock_cur

        site_dict = {
            'data_dir': 'value1',
        }

        mock_yaml2dict.return_value = site_dict

        exited = False
        try:
            upgrade_db.main('config_PAR_008_GV.yml')
        except SystemExit:
            exited = True
        assert exited is True
        mock_cur.execute.assert_not_called()
        mock_con.commit.assert_not_called()
        mock_cur.close.assert_called_once()
        mock_con.close.assert_called_once()
