from .abstractcam import AbstractCamera
import numpy as np
import cv2


class VrepVisionSensor(AbstractCamera):
    registers = AbstractCamera.registers
    simulator_only = True

    def __init__(self, name, fps, vrep_io):
        try:
            vision_sensor_handler = vrep_io.get_object_handle(name)
        except:
            raise Exception('Can not load ' + name + ' from V-REP')
        self._res, image = vrep_io.get_vision_sensor_image(vision_sensor_handler, False)
        self._vrep_io = vrep_io
        self._vision_sensor_handler = vision_sensor_handler
        self._last_frame = None
        AbstractCamera.__init__(self, name, self._res, fps)

    def _get_image_from_vrep(self):
        self._vrep_io.enable_syncronous_mode(True)
        vrep_image = self._vrep_io.get_vision_sensor_image(self._vision_sensor_handler)
        self._vrep_io.enable_syncronous_mode(False)
        return vrep_image

    def grab(self):
        """v-rep image grab
        :returns formatted image as array of BGR values
        """
        self._res, image = self._get_image_from_vrep()
        if image is None:
            return self._last_frame
        image = np.array(image, dtype=np.uint8)
        try:
            image.resize([self._res[0], self._res[1], 3])
            image = np.rot90(image, 2)
            image = np.fliplr(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except ValueError:
            return self._last_frame
        return image
