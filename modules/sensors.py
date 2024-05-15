import sys
from abc import abstractmethod, ABC
from enum import Enum
from time import sleep

import serial


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
    def init_serial_connection(self, port: int, baud: int, logger):
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
