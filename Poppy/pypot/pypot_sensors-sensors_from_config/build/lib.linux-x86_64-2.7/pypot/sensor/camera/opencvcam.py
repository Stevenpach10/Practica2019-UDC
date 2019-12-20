import cv2

from .abstractcam import AbstractCamera
from threading import Thread
from time import time


class OpenCVCamera(AbstractCamera):
    registers = AbstractCamera.registers + ['index']

    def __init__(self, name, index, fps, resolution=None):
        self._index = index
        self.capture = cv2.VideoCapture(index)
        if resolution is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        if not self.capture.isOpened():
            raise ValueError(
                'Can not open camera device {}. You should start your robot with argument camera=\'dummy\'. E.g. p = PoppyErgoJr(camera=\'dummy\')'.format(
                    index))
        self.running = True
        AbstractCamera.__init__(self, name, resolution, fps)
        self._processing = Thread(target=self._process_loop)
        self._processing.daemon = True
        self._processing.start()
        self._last_frame = None
        self._not_initialized = True
        while self._not_initialized:
            pass

    @property
    def frame(self):
        # return self.grab()
        return self._last_frame

    @property
    def index(self):
        return self._index

    def grab(self):
        """OpenCV image grab
        :returns formatted image as array of BGR values
        """
        rval, frame = self.capture.read()
        if not rval:
            raise EnvironmentError('Can not grab image from the camera!')
        return frame

    def post_processing(self, image):
        return image

    def _grab_and_process(self):
        return self.post_processing(self.grab())

    def _process_loop(self):
        period = 1.0 / self.fps
        last_frame_time = time()
        self._last_frame = self._grab_and_process()
        self._not_initialized = False
        while self.running:
            if time() - last_frame_time > period:
                self._last_frame = self._grab_and_process()
                last_frame_time = time()

    def close(self):
        self.running = False
        self._processing.join()
        AbstractCamera.close(self)
        self.capture.release()
