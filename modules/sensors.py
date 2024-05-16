"""
Module containing the abstract class for sensors,
and the implementations of different sensor
classes inheriting this class
"""
import sys
from abc import abstractmethod, ABC
from enum import Enum
import time

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
    def init_serial_connection(self, port: str, baud: int, logger):
        """
        Abstract function for initializing
        the serial connection with the sensor
        :param port:
        :param baud:
        :param logger:
        """

    @abstractmethod
    def sensor_start_sequence(self, config_dict, logger):
        """
        Abstract function for executing the startup sequence for a sensor.
        This function performs the necessary initialization steps to configure a
        sensor with specific settings provided in the `config_dict`. It
        logs each step of the process using the provided `logger` object.
        :param config_dict: Dictionary containing configuration parameters
                            for the sensor.
        :param logger: Logger for logging information and errors
        """

    @abstractmethod
    def write(self, msg, logger):
        """
        Abstract function for sending
        a message to the sensor
        :param msg: message for the sensor
        :param logger: logger for errors
        """

    @abstractmethod
    def read(self, logger):
        """
        Abstract function for reading
        lines from the sensor
        :param logger: logger for errors
        """

    @abstractmethod
    def get_type(self) -> str:
        """
        Returns the type of the sensor as a string
        """


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
        self.serial_connection: serial.Serial = None

    def init_serial_connection(self, port: str, baud: int, logger):
        """
        Initializes the serial connection with the sensor
        :param port:
        :param baud:
        :param logger:
        """
        try:
            parsivel = serial.Serial(port, baud, timeout=1)  # Defines the serial port
            logger.info(msg=f'Connected to parsivel, via: {parsivel}')
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(msg=e)
            sys.exit()
        self.serial_connection = parsivel

    def sensor_start_sequence(self, config_dict, logger):
        """
        Executes the startup sequence for the Parsivel sensor.
        This function performs the necessary initialization steps to configure the
        Parsivel sensor with specific settings provided in the `config_dict`. It
        logs each step of the process using the provided `logger` object.
        :param config_dict: Dictionary containing configuration parameters
                            for the sensor.
        :param logger: Logger for logging information and errors
        """
        logger.info(msg="Starting parsivel start sequence commands")
        self.serial_connection.reset_input_buffer()  # Flushes input buffer

        # Sets the name of the Parsivel, maximum 10 characters
        parsivel_set_station_code = ('CS/K/' + config_dict['station_code'] + '\r').encode('utf-8')
        self.write(parsivel_set_station_code, logger)
        time.sleep(1)

        # Sets the ID of the Parsivel, maximum 4 numerical characters
        parsivel_set_id = ('CS/J/'
                           + config_dict['global_attrs']['sensor_name']
                           + '\r').encode('utf-8')
        self.write(parsivel_set_id, logger)
        time.sleep(2)

        parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
        self.write(parsivel_restart, logger)  # resets rain amount
        time.sleep(10)

        # The Parsivel broadcasts the user defined telegram.
        parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')
        self.write(parsivel_user_telegram, logger)

    def write(self, msg, logger):
        """
        If the serial connection is initialized ->
        executes the write function for the
        serial connection with the respective message,
        else -> sends an error through the logger
        :param msg: message for the sensor
        :param logger: logger for errors
        :return: None
        """
        if self.serial_connection is not None:
            self.serial_connection.write(msg)
            return None
        logger.error(msg="serial_connection not initialized")
        return None

    def read(self, logger):
        """
        If the serial connection is initialized ->
        read and return a list lines from the sensor
        else -> write an error through the logger
        :param logger: logger for errors
        :return: list of lines or None
        """
        if self.serial_connection is not None:
            parsivel_lines = self.serial_connection.readlines()
            return parsivel_lines
        logger.error(msg="serial_connection not initialized")
        return None

    def get_type(self) -> str:
        """
        Returns the type of the sensor
        :return: type of the serial as a string
        """
        return self.sensor_type.value
