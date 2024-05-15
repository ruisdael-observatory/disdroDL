import sys
from abc import abstractmethod, ABC
from enum import Enum
from time import sleep

import serial

from modules.now_time import NowTime


class SensorType(Enum):
    """
    Enum class for the different types of sensors
    """
    PARSIVEL = "parsivel"
    THIES = "thies"


class Sensor(ABC):
    """
    Abstract class for outlining the commonly
    used functionality for different types of sensors
    """

    def __init__(self, sensor_type: SensorType):
        """
        Constructor for sensors
        :param sensor_type: type of the serial_connection (enum)
        """
        self.sensor_type = sensor_type

    @abstractmethod
    def init_serial_connection(self, port: str, baud: int, logger):
        """

        :param port:
        :param baud:
        :param logger:
        """
        pass

    @abstractmethod
    def sensor_start_sequence(self, config_dict, logger):
        """

        :param serial_connection:
        :param config_dict:
        :param logger:
        """
        pass

    @abstractmethod
    def write(self, msg, logger):
        """

        :param msg:
        :param logger:
        """
        pass

    @abstractmethod
    def read(self, logger):
        """

        :param logger:
        """
        pass

    @abstractmethod
    def get_type(self) -> str:
        """
        Returns the type of the serial_connection
        """
        pass

    @abstractmethod
    def get_serial_connection(self):
        pass


class Parsivel(Sensor):
    """
    Class inheriting Sensor and representing
    the parsivel type serial_connection
    """

    def __init__(self, sensor_type=SensorType.PARSIVEL):
        """
        Constructor for the parsivel type serial_connection
        :param sensor_type: type of the serial_connection (enum)
        """
        super().__init__(sensor_type)
        self.serial_connection: serial.Serial = None

    # has to be deleted from util_functionalities.py
    def init_serial_connection(self, port: int, baud: int, logger):
        """

        :param port:
        :param baud:
        :param logger:
        """
        try:
            parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
            logger.info(msg=f'Connected to parsivel, via: {parsivel}')
        except Exception as e:
            logger.error(msg=e)
            sys.exit()
        self.serial_connection = parsivel

    # has to be deleted from util_functionalities.py
    def sensor_start_sequence(self, config_dict, logger):
        """

        :param serial_connection:
        :param config_dict:
        :param logger:
        """
        logger.info(msg="Starting parsivel start sequence commands")
        self.serial_connection.reset_input_buffer()  # Flushes input buffer

        # Sets the name of the Parsivel, maximum 10 characters
        parsivel_set_station_code = ('CS/K/' + config_dict['station_code'] + '\r').encode('utf-8')
        self.serial_connection.write(parsivel_set_station_code)
        sleep(1)

        # Sets the ID of the Parsivel, maximum 4 numerical characters
        parsivel_set_ID = ('CS/J/' + config_dict['global_attrs']['sensor_name'] + '\r').encode('utf-8')
        self.serial_connection.write(parsivel_set_ID)
        sleep(2)

        parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
        self.serial_connection.write(parsivel_restart)  # resets rain amount
        sleep(10)

        # The Parsivel broadcasts the user defined telegram.
        parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')
        self.serial_connection.write(parsivel_user_telegram)

    def write(self, msg, logger):
        """

        :param msg:
        :param logger:
        :return:
        """
        if self.serial_connection is not None:
            self.serial_connection.write(msg)
            return None
        else:
            logger.error(msg="serial_connection not initialized")
            return None

    def read(self, logger):
        """

        :param logger:
        :return:
        """
        if self.serial_connection is not None:
            return self.serial_connection.readlines()
        else:
            logger.error(msg="serial_connection not initialized")
            return None

    def get_type(self) -> str:
        """
        Returns the type of the serial_connection
        :return:
        """
        return self.sensor_type.value

    def get_serial_connection(self):
        return self.serial_connection


class Thies(Sensor):
    """
    Class inheriting Sensor and representing the thies sensor
    """

    def __init__(self, sensor_type=SensorType.THIES, thies_id='00'):
        """
        Constructor for the thies type serial_connection
        :param sensor_type: type of the serial_connection (enum)
        """
        super().__init__(sensor_type)
        self.serial_connection: serial.Serial = None
        self.thies_id = thies_id

    def init_serial_connection(self, port, baud, logger):
        """
        Initializes the serial connection for the thies sensor
        :param port: the port where the thies is connected to
        :param baud: the baudrate of the thies
        :param logger: the logger object
        """
        try:
            thies = serial.Serial(port, baud, timeout=1)  # Defines the serial port
            logger.info(msg=f'Connected to parsivel, via: {thies}')
            self.serial_connection = thies
        except Exception as e:
            logger.error(msg=e)
            sys.exit()


    def sensor_start_sequence(self, config_dict, logger):
        """
        Send the serial commands to the thies that changes the necessary parameters
        :param config_dict: the configuration dictionary
        :param logger: the logger object
        """
        self.serial_connection.reset_input_buffer()
        self.serial_connection.reset_output_buffer()

        logger.info(msg="Starting thies start sequence commands")

        thies_config_mode_enable = ('\r' + self.thies_id + 'KY00001\r').encode('utf-8')
        self.write(thies_config_mode_enable, logger)  # place in config mode
        sleep(1)

        thies_automatic_mode_on = ('\r' + self.thies_id + 'TM00000\r').encode('utf-8')
        self.write(thies_automatic_mode_on, logger)  # turn of automatic mode
        sleep(1)

        thies_set_hours = ('\r' + self.thies_id + 'ZH000' + NowTime().time_list[0] + '\r').encode('utf-8')
        self.write(thies_set_hours, logger)  # set hour
        sleep(1)

        thies_set_minutes = ('\r' + self.thies_id + 'ZM000' + NowTime().time_list[1] + '\r').encode('utf-8')
        self.write(thies_set_minutes, logger)  # set minutes
        sleep(1)

        thies_set_seconds = ('\r' + self.thies_id + 'ZS000' + NowTime().time_list[2] + '\r').encode('utf-8')
        self.write(thies_set_seconds, logger)  # set seconds
        sleep(1)

        thies_config_mode_disable = ('\r' + self.thies_id + 'KY00000\r').encode('utf-8')
        self.write(thies_config_mode_disable, logger)  # place out of config mode
        sleep(1)

        self.serial_connection.reset_input_buffer()
        self.serial_connection.reset_output_buffer()

    def write(self, msg, logger):
        """
        Writes the message to the serial connection
        :param msg: The message to send over the serial connection
        :param logger: the logger object
        """
        if self.serial_connection is None:
            logger.error(msg="serial_connection not initialized")
        else:
            self.serial_connection.write(msg)

    def read(self, logger):
        """
        Reads the data sent by the thies sensor
        :param logger: the logger object
        :return: the read line from the thies sensor
        """
        if self.serial_connection is None:
            logger.error(msg="serial_connection not initialized")
            return None

        sleep(2)  # Give sensor some time to create the telegram
        return self.serial_connection.readline()

    def get_type(self):
        """
        Returns the type of the serial_connection
        :return: the type of the serial_connection
        """
        return self.sensor_type

    def get_serial_connection(self):
        """
        Returns the serial connection
        :return: the serial connection object
        """
        return self.serial_connection
