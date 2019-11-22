from ...robot.sensor import Sensor

class ProximitySensor(Sensor):
    registers = Sensor.registers + ['detected', 'detected_point', 'detected_object_handle', 'detected_surface']
    simulator_only = True

    def __init__(self, name, vrep_io):
        try:
            proximity_sensor_handler = vrep_io.get_object_handle(name)
        except:
            raise Exception('Can not load ' + name + ' from V-REP')
        vrep_io.call_remote_api('simxReadProximitySensor', proximity_sensor_handler, streaming=True)

        # add error handler
        def scan():
            return vrep_io.call_remote_api('simxReadProximitySensor', proximity_sensor_handler, buffer=True)

        self._scan = scan
        self._detected = False
        self._detected_point = [-1.0, -1.0, -1.0]
        self._detected_object_handle = None
        self._detected_surface = [-1.0, -1.0, -1.0]
        Sensor.__init__(self, name)

    @property
    def detected(self):
        return self._detected

    @property
    def detected_point(self):
        return self._detected_point

    @property
    def detected_object_handle(self):
        return self._detected_object_handle

    @property
    def detected_surface(self):
        return self._detected_surface

    def scan(self):
        result = self._scan()
        self._detected, self._detected_point, self._detected_object_handle, self._detected_surface = result
        return result
