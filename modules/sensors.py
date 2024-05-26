"""
Module containing the abstract class for sensors,
and the implementations of different sensor
classes inheriting this class
"""
import sys
from abc import abstractmethod, ABC
from enum import Enum
from time import sleep

import serial

from modules.now_time import NowTime  # pylint: disable=import-error


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
        :param port: the port where the sensor is connected to
        :param baud: the baudrate of the sensor
        :param logger: Logger for logging information and errors
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
    def reset_sensor(self, logger, factory_reset: bool):
        """
        Abstract function for reseting a sensor.
        :param logger: Logger for logging information
        :param factory_reset: Whether the factory reset should be performed
        """

    @abstractmethod
    def close_serial_connection(self):
        """
        Abstract function for closing the serial connection
        """

    @abstractmethod
    def write(self, msg, logger):
        """
        Abstract function for sending
        a message to the sensor
        :param msg: Message for the sensor
        :param logger: Logger for errors
        """

    @abstractmethod
    def read(self, logger):
        """
        Abstract function for reading
        lines from the sensor
        :param logger: Logger for errors
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
        :param port: the port where the parsivel sensors is connected to
        :param baud: the baudrate of the parsivel sensor
        :param logger: Logger for logging information and errors
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
        sleep(1)

        # Sets the ID of the Parsivel, maximum 4 numerical characters
        parsivel_set_id = ('CS/J/'
                           + config_dict['global_attrs']['sensor_name']
                           + '\r').encode('utf-8')
        self.write(parsivel_set_id, logger)
        sleep(2)

        parsivel_restart = 'CS/Z/1\r'.encode('utf-8')
        self.write(parsivel_restart, logger)  # resets rain amount
        sleep(10)

        # The Parsivel broadcasts the user defined telegram.
        parsivel_user_telegram = 'CS/M/M/1\r'.encode('utf-8')
        self.write(parsivel_user_telegram, logger)

    def reset_sensor(self, logger, factory_reset: bool):
        """
        Abstract function for reseting a sensor.
        :param logger: Logger for logging information
        :param factory_reset: Whether the factory reset should be performed
        """
        logger.info(msg="Reseting Parsivel")
        if factory_reset:
            parsivel_reset_code = 'CS/F/1\r'.encode('utf-8')
            self.write(parsivel_reset_code, logger)
        else:
            parsivel_restart = 'CS/Z/1\r'.encode('utf-8')  # restart
            self.write(parsivel_restart, logger)
        sleep(5)

    def close_serial_connection(self):
        """
        Closes the serial connection
        """
        if self.serial_connection is not None:
            self.serial_connection.close()

    def write(self, msg, logger):
        """
        If the serial connection is initialized ->
        executes the write function for the
        serial connection with the respective message,
        else -> sends an error through the logger
        :param msg: Message for the sensor
        :param logger: Logger for errors
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
        :return: List of lines or None
        """
        if self.serial_connection is not None:
            self.write('CS/PA\r\n'.encode('ascii'))
            parsivel_lines = self.serial_connection.readlines()
            return parsivel_lines
        logger.error(msg="serial_connection not initialized")
        return None

    def get_type(self) -> str:
        """
        Returns the type of the sensor
        :return: Type of the serial as a string
        """
        return self.sensor_type.value


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
            thies = serial.Serial(port, baud, timeout=5)  # Defines the serial port
            logger.info(msg=f'Connected to parsivel, via: {thies}')
            self.serial_connection = thies
        except Exception as e:  # pylint: disable=broad-exception-caught
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

    def reset_sensor(self, logger, factory_reset: bool):
        """
        Resets the thies sensor
        :param logger: the logger object
        :param factory_reset: whether the factory reset should be performed
        """
        logger.info(msg="Resetting Thies")

        # place in config mode
        self.write(f'\r{self.thies_id}KY00001\r'.encode('utf-8'), logger)
        sleep(1)

        # Restart the sensor
        self.write(f'\r{self.thies_id}RS00001\r'.encode('utf-8'), logger)
        sleep(60)

        # Reset error counters
        self.write(f'\r{self.thies_id}RF00001\r'.encode('utf-8'), logger)
        sleep(1)

        # Reset precipitation quantity and duration of quantity measurement
        self.write(f'\r{self.thies_id}RA00001\r'.encode('utf-8'), logger)
        sleep(1)

        # Place out of config mode
        self.write(f'\r{self.thies_id}KY00000\r'.encode('utf-8'), logger)
        sleep(1)

        logger.info(msg="Thies reset complete")

    def close_serial_connection(self):
        """
        Closes the serial connection
        """
        if self.serial_connection is not None:
            self.serial_connection.close()

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
        self.serial_connection.write(f'\r{self.thies_id}TR00005\r'.encode('utf-8'))
        output = self.serial_connection.readline()
        decoded = str(output[0:len(output) - 2].decode("utf-8"))
        return decoded

    def get_type(self):
        """
        Returns the type of the serial_connection
        :return: the type of the serial_connection
        """
        return self.sensor_type
