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
        :param sensor_type: type of the sensor (enum)
        """
        self.sensor_type = sensor_type

    @abstractmethod
    def init_serial(self, port: int, baud: int, logger):
        """

        :param port:
        :param baud:
        :param logger:
        """
        pass

    @abstractmethod
    def sensor_start_sequence(self, serial_connection, config_dict, logger):
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
        Returns the type of the sensor
        """
        pass


class Parsivel(Sensor):
    """
    Class inheriting Sensor and representing
    the parsivel type sensor
    """
    def __init__(self, sensor_type=SensorType.PARSIVEL):
        """
        Constructor for the parsivel type sensor
        :param sensor_type: type of the sensor (enum)
        """
        super().__init__(sensor_type)
        self.sensor: serial.Serial = None

    # has to be deleted from util_functionalities.py
    def init_serial(self, port: int, baud: int, logger):
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
        self.sensor = parsivel

    # has to be deleted from util_functionalities.py
    def sensor_start_sequence(self, serial_connection, config_dict, logger):
        """

        :param serial_connection:
        :param config_dict:
        :param logger:
        """
        logger.info(msg="Starting parsivel start sequence commands")
        serial_connection.reset_input_buffer()  # Flushes input buffer
        # Sets the name of the Parsivel, maximum 10 characters
        parsivel_set_station_code = ('CS/K/' + config_dict['station_code'] + '\r').encode('utf-8')
        serial_connection.write(parsivel_set_station_code)
        sleep(1)
        # Sets the ID of the Parsivel, maximum 4 numerical characters
        parsivel_set_ID = ('CS/J/' + config_dict['global_attrs']['sensor_name'] + '\r').encode('utf-8')
        serial_connection.write(parsivel_set_ID)
        sleep(2)
        parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
        serial_connection.write(parsivel_restart)  # resets rain amount
        sleep(10)
        # The Parsivel broadcasts the user defined telegram.
        parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')
        serial_connection.write(parsivel_user_telegram)

    def write(self, msg, logger):
        """

        :param msg:
        :param logger:
        :return:
        """
        if self.sensor is not None:
            self.sensor.write(msg)
            return None
        else:
            logger.error(msg="sensor not initialized")
            return None

    def read(self, logger):
        """

        :param logger:
        :return:
        """
        if self.sensor is not None:
            return self.sensor.readlines()
        else:
            logger.error(msg="sensor not initialized")
            return None

    def get_type(self) -> str:
        """
        Returns the type of the sensor
        :return:
        """
        return self.sensor_type.value
