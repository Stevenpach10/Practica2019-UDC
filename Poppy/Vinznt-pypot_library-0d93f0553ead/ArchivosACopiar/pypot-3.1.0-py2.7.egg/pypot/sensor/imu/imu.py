from ...dynamixel import get_available_ports
from serial import Serial, SerialException
from ...robot.sensor import Sensor
from time import sleep, time
from threading import Thread


def connect_to_serial_imu(port):
    try:
        # test the port
        serial_device = Serial(port, 57600, timeout=0.1)
        sleep(2)
        if is_imu_device(serial_device):
            return serial_device
        else:
            return None
    except SerialException:
        return None


def is_imu_device(serial_device):
    initial_serial_line = serial_device.readline()
    if len(initial_serial_line) > 0:
        if initial_serial_line.startswith('ITG'):
            serial_device.write('4')
            return True
        else:
            return False
    else:
        return False


def parse_imu_raw_data(line):
    invalid_data = False, ()
    if len(line) > 0:
        if line.endswith('#\r\n'):
            line = line.replace('$', '', 1)
            line = line.replace('#\r\n', '', 1)
            line = line.split(',')
            try:
                values = map(int, line)
            except ValueError:
                return invalid_data
            if len(values[6:9]) == 3:
                return True, (values[0:3], values[3:6], values[6:9])
            else:
                return invalid_data
        else:
            return invalid_data
    else:
        return invalid_data


class IMU(Sensor):
    registers = Sensor.registers + ['accelerometer', 'gyroscope', 'magnetometer']

    def __init__(self, name, frequency=30, port='auto'):
        Sensor.__init__(self, name)
        self._serial_device = None
        if port == 'auto':
            # get the list of ports
            available_ports = get_available_ports(only_free=True)
            for available_port in available_ports:
                self._serial_device = connect_to_serial_imu(available_port)
                if self._serial_device is not None:
                    break
        else:
            self._serial_device = connect_to_serial_imu(port)
        if self._serial_device is None:
            raise Exception('Can not connect with IMU')

        # initialisation of all properties
        self._accelerometer = [0.0, 0.0, 0.0]
        self._gyroscope = [0.0, 0.0, 0.0]
        self._magnetometer = [0.0, 0.0, 0.0]
        # control flag of the main loop
        self._sync_freq = frequency
        self.running = True
        self._sync = Thread(target=self._sync_loop)
        self._sync.daemon = True
        self._sync.start()

    @property
    def accelerometer(self):
        return self._accelerometer

    @property
    def gyroscope(self):
        return self._gyroscope

    @property
    def magnetometer(self):
        return self._magnetometer

    def _sync_loop(self):
        period = 1.0 / self._sync_freq
        last_loop_time = time()
        while self.running:
            if time() - last_loop_time > period:
                self._serial_device.reset_input_buffer()
                line = self._serial_device.readline()
                is_valid_data, data = parse_imu_raw_data(line)
                if is_valid_data:
                    self._accelerometer, self._gyroscope, self._magnetometer = data
                last_loop_time = time()

    def close(self):
        self.running = False
        # wait the main loop is finished
        self._sync.join()
        self._serial_device.close()
        sleep(1)
