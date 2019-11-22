from serial import Serial
from time import sleep
from threading import Thread
from ...robot.sensor import Sensor

# OUTPUT MESSAGES
MOVE_MOTORS_MESSAGE_CODE = 0x01
PLAY_SOUND_MESSAGE_CODE = 0x02
CONFIG_FREQUENCY_MESSAGE_CODE = 0x03
ODROID_ACK_MESSAGE_CODE = 0x10
# INPUT MESSAGES
STATUS_MESSAGE_CODE = 0x00
ARDUINO_ACK_MESSAGE_CODE = 0x11
INPUT_MESSAGES_CODES = [STATUS_MESSAGE_CODE, ARDUINO_ACK_MESSAGE_CODE]
# MESSAGE SIZES
MOVE_MOTORS_MESSAGE_SIZE = 0x0b
PLAY_SOUND_MESSAGE_SIZE = 0x04
CONFIG_FREQUENCY_MESSAGE_SIZE = 0x05
ODROID_ACK_MESSAGE_SIZE = 0x00
# HEADER START VALUES
HEADER_START_VALUE = 0x7e
OUTPUT_HEADER_START_VALUE = 0x7c
# HEADER VALUES POSITIONS
HEADER_START_CODE = 0
HEADER_MESSAGE_TYPE = 1
HEADER_DATA_SIZE = 2
HEADER_CHECKSUM = 3


def split_value(value, start, end):
    return int(("%020x" % value)[start:end], 16)


def generate_checksum(buffer_list):
    value = 0
    for byte in range(0, len(buffer_list) - 1):
        value = value + buffer_list[byte]
    return split_value(value, -2, None)


def valid_checksum(buffer_list):
    return generate_checksum(buffer_list) == buffer_list[-1]  # checksum value & 0xFF


def is_valid_header_message_type(message_type):
    if message_type in INPUT_MESSAGES_CODES:
        return True
    else:
        return False


def parse_bytes_to_number(bytes_array):
    value = 0
    for byte in bytes_array:
        value = value << 8
        value += byte
    return value


def get_array_value(array, position):
    if position < len(array):
        return array[position]
    else:
        return 0


class Sender(object):
    """Class designed for sending messages via serial communication"""
    def __init__(self, arduino):
        # type: (Serial) -> None
        """Class Initializer
        :param arduino:
        """
        self.arduino = arduino
        self.output_header_buffer_size = 4
        self._output_header_buffer = [0] * self.output_header_buffer_size
        self._header_start_code = OUTPUT_HEADER_START_VALUE
        self._output_header_buffer[HEADER_START_CODE] = self._header_start_code
        self._output_data_buffer = []

    def _clear_output_buffers(self):
        """Reset output buffers to initial state"""
        self._output_header_buffer = [0] * self.output_header_buffer_size
        self._output_header_buffer[HEADER_START_CODE] = self._header_start_code
        self._output_data_buffer = []

    def _fill_header(self, message_code, data_size):
        # type: (int, int) -> None
        """Fills the header output buffer with info related to the message
        :param message_code: code of the data message that gotta be send
        :param data_size: size of the message data
        """
        self._output_header_buffer[HEADER_MESSAGE_TYPE] = message_code
        self._output_header_buffer[HEADER_DATA_SIZE] = data_size
        self._output_header_buffer[HEADER_CHECKSUM] = generate_checksum(self._output_header_buffer)

    def _send_data(self):
        """Sends the whole message (header + data) via serial communication """
        array_bytes = ''.join(chr(byte) for byte in(self._output_header_buffer + self._output_data_buffer))
        self.arduino.write(array_bytes)
        self._clear_output_buffers()

    def _initialize_output_data(self, data_size):
        # type: (int) -> None
        """Initializes output message data buffer
        :param data_size: Size of the output message data
        """
        self._output_data_buffer = [0] * data_size

    def _generate_output_data_checksum(self):
        """Generates message data checksum"""
        self._output_data_buffer[-1] = generate_checksum(self._output_data_buffer)

    def move_motors(self, motor1_dir, motor2_dir, motor1_position, motor2_position):
        # type: (int, int, int, int) -> None
        """Sends a message to move the motors
        :param motor1_dir: motor1 new direction
        :param motor2_dir: motor2 new direction
        :param motor1_position: motor1 new position
        :param motor2_position: motor2 new position
        """
        self._fill_header(MOVE_MOTORS_MESSAGE_CODE, MOVE_MOTORS_MESSAGE_SIZE)
        self._initialize_output_data(MOVE_MOTORS_MESSAGE_SIZE)
        self._output_data_buffer[0] = motor1_dir
        self._output_data_buffer[1] = motor2_dir
        self._output_data_buffer[2] = split_value(motor1_position, -8, -6)
        self._output_data_buffer[3] = split_value(motor1_position, -6, -4)
        self._output_data_buffer[4] = split_value(motor1_position, -4, -2)
        self._output_data_buffer[5] = split_value(motor1_position, -2, None)
        self._output_data_buffer[6] = split_value(motor2_position, -8, -6)
        self._output_data_buffer[7] = split_value(motor2_position, -6, -4)
        self._output_data_buffer[8] = split_value(motor2_position, -4, -2)
        self._output_data_buffer[9] = split_value(motor2_position, -2, None)
        self._generate_output_data_checksum()
        self._send_data()

    def play_sound(self, track, length):
        # type: (int, int) -> None
        """Sends a message to play a track
        :param track: track number
        :param length: track length
        """
        self._fill_header(PLAY_SOUND_MESSAGE_CODE, PLAY_SOUND_MESSAGE_SIZE)
        self._initialize_output_data(PLAY_SOUND_MESSAGE_SIZE)
        self._output_data_buffer[0] = split_value(track, -2, None)
        self._output_data_buffer[1] = split_value(length, -4, -2)
        self._output_data_buffer[2] = split_value(length, -2, None)
        self._generate_output_data_checksum()
        self._send_data()

    def config_frequency(self, frequency):
        # type: (int) -> None
        """Sends a message to change the frequency of the status message sent by the arduino"""
        self._fill_header(CONFIG_FREQUENCY_MESSAGE_CODE, CONFIG_FREQUENCY_MESSAGE_SIZE)
        self._initialize_output_data(CONFIG_FREQUENCY_MESSAGE_SIZE)
        self._output_data_buffer[0] = split_value(frequency, -8, -6)
        self._output_data_buffer[1] = split_value(frequency, -6, -4)
        self._output_data_buffer[2] = split_value(frequency, -4, -2)
        self._output_data_buffer[3] = split_value(frequency, -2, None)
        self._generate_output_data_checksum()
        self._send_data()

    def send_ack_message(self):
        """Sends received confirmation message"""
        self._fill_header(ODROID_ACK_MESSAGE_CODE, ODROID_ACK_MESSAGE_SIZE)
        self._send_data()


class Receiver(object):
    def __init__(self, arduino, verbose):
        self.arduino = arduino
        self._verbose = verbose
        self._input_header_buffer = []
        self._input_data_buffer = []
        self._input_header_size = 4
        self._input_header_found = False
        self._is_header = False
        self._header_start_code = HEADER_START_VALUE
        self.running = True
        self._capacitives = []
        self._microphones = []
        self._motors_position = []

    def get_capacitive_value(self, capacitive_number):
        if capacitive_number < len(self._capacitives):
            return True if self._capacitives[capacitive_number] == 1 else False
        else:
            return False

    def get_microphone_value(self, microphone_number):
        get_array_value(self._microphones, microphone_number)

    def get_motor_position(self, motor_number):
        get_array_value(self._motors_position, motor_number)

    def _clear_input_buffers(self):
        self._input_header_buffer = []
        self._input_data_buffer = []

    def _reset_data(self):
        """Clean input buffers and reset control flags"""
        self._clear_input_buffers()
        self._input_header_found = False
        self._is_header = False

    def _get_byte(self):
        """Reads a byte from serial communication"""
        input_data = self.arduino.read(1)
        if len(input_data) > 0:
            return ord(input_data)
        return None

    def _process_incoming_message(self):
        """Process the received message in function of his type"""
        if self._input_header_buffer[HEADER_MESSAGE_TYPE] == STATUS_MESSAGE_CODE:
            self._capacitives = self._input_data_buffer[:4]
            self._microphones = [parse_bytes_to_number(self._input_data_buffer[4:8]),
                                 parse_bytes_to_number(self._input_data_buffer[8:12])]
            self._motors_position = [parse_bytes_to_number(self._input_data_buffer[12:14]),
                                     parse_bytes_to_number(self._input_data_buffer[14:16])]
            if self._verbose:
                print ('--------')
                print ('data')
                print ('capacitives')
                print (self._capacitives)
                print ('microphones')
                print (self._microphones)
                print ('motors')
                print (self._motors_position)
                print ('*******')
        elif self._input_header_buffer[HEADER_MESSAGE_TYPE] == ARDUINO_ACK_MESSAGE_CODE:
            if self._verbose:
                print ('Arduino ack message')

    def _is_valid_data_message(self, buffer_size):
        """Gets fills data buffer to verify if it's a valid message
        :param buffer_size: Buffer size that was received in header message
        :return: Boolean that indicates whether the message is valid or not
        """
        if buffer_size == 0:  # message without data
            self._process_incoming_message()
            return True
        while buffer_size > 0:
            hex_input = self._get_byte()
            if hex_input is not None:
                self._input_data_buffer.append(hex_input)
                buffer_size -= 1
        if valid_checksum(self._input_data_buffer):
            self._process_incoming_message()
            return True
        else:
            # invalid data
            return False

    def _check_header_start(self, byte):
        """Awaits for the header start byte. If a start byte wasn't read previously
        that means a new message was received
        :param byte: byte read
        """
        if byte == self._header_start_code:
            if not self._input_header_found:
                self._is_header = True
                self._input_header_found = True
                self._clear_input_buffers()

    def _header_buffer_full(self):
        """ Indicates if the input header is full"""
        return len(self._input_header_buffer) == self._input_header_size

    def loop(self):
        """Process every byte from serial input"""
        while self.running:
            hex_input = self._get_byte()
            if hex_input is not None:
                self._check_header_start(hex_input)
                self._input_header_buffer.append(hex_input)
                if self._header_buffer_full():
                    if self._verbose:
                        print (self._input_header_buffer)
                    if (valid_checksum(self._input_header_buffer)
                            and
                            is_valid_header_message_type(self._input_header_buffer[HEADER_MESSAGE_TYPE])):
                        self._is_valid_data_message(self._input_header_buffer[HEADER_DATA_SIZE])
                    self._reset_data()


class ArduinoSensor(Sensor):
    """Class to handle the protocol communication with """
    registers = Sensor.registers + ['port', 'baud']

    def __init__(self, name, port, baud, verbose=False):
        # type: (str, int, int) -> None
        """Initializes ArduinoSensor class
        :param name: sensor name
        :param port: serial connection port
        :param baud: serial connection baud
        """
        Sensor.__init__(self, name)
        self.port = port
        self.baud = baud
        self._arduino = None
        self._receiver = None
        self._sender = None
        self._status_loop = None
        self.running = False
        self.start(verbose)

    def start(self, verbose):
        """ Establishes a new serial connection to begin the receiver and sender threads"""
        self._arduino = Serial(self.port, self.baud, timeout=0.03)  # Windows
        sleep(1)  # give the connection a second to settle
        self._receiver = Receiver(self._arduino, verbose)
        self._sender = Sender(self._arduino)
        self._status_loop = Thread(target=self._receiver.loop)
        self._status_loop.daemon = True
        self._status_loop.start()
        self.running = True

    def send_move_motors_message(self, motor1_dir, motor2_dir, motor1_position, motor2_position):
        # type: (int, int, int, int) -> None
        """Sends a message to move the motors
        :param motor1_dir: motor1 new direction
        :param motor2_dir: motor2 new direction
        :param motor1_position: motor1 new position
        :param motor2_position: motor2 new position
        """
        self._sender.move_motors(motor1_dir, motor2_dir, motor1_position, motor2_position)

    def send_play_sound_message(self, track, length):
        # type: (int, int) -> None
        """Sends a message to play a track
        :param track: track number
        :param length: track length
        """
        self._sender.play_sound(track, length)

    def send_config_frequency_message(self, frequency):
        # type: (int) -> None
        """Sends a message to change the frequency of the status message sent by the arduino"""
        self._sender.config_frequency(frequency)

    def send_ack_message(self):
        """Sends received confirmation message"""
        self._sender.send_ack_message()

    def close(self):
        """Closes all arduino communication"""
        self.running = False
        self._receiver.running = False
        self._status_loop.join()
        self._arduino.close()
