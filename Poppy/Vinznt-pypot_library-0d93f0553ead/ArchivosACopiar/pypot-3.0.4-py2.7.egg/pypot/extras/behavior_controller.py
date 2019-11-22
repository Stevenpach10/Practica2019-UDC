from threading import Thread
from .tracker import Tracker
from .image_display import ImageDisplay
from time import time
from warnings import warn
try:
    from .recognition import FaceRecognition
except ImportError:
    warn("FaceRecognition can't be imported. Missing Dependencies.")

from ..creatures.abstractcreature import actual_robot

if not actual_robot:
    raise AttributeError('Intitialize a robot to use the tracker')


def close_thread(thread):
    if thread is not None:
        thread.join()
        thread = None


class BehaviorController(object):
    def __init__(self, camera, get_capacitive_function=None):
        self._display = None
        self._camera = camera
        self._face_recognition = None
        self._tracker = None
        self._is_capacitive_enabled = get_capacitive_function
        self._recognizer_frequency = 0.5
        self._face_recognized = False
        self._running = False
        self._search = False
        self._track_object = False
        # behavior threads
        self._recognizer_thread = None
        self._greeting_thread = None
        self._tracker_thread = None

    @property
    def display(self):
        return self._display

    @property
    def face_recognition(self):
        return self._face_recognition

    def _start_thread(self, thread, target_function, thread_name, args=None, force=False):
        if not self._running or force:
            thread = Thread(target=target_function, name=thread_name, args=args)
            thread.daemon = True
            self._running = True
            thread.start()

    # DISPLAY

    def start_display(self, animations, default_animation):
        self._display = ImageDisplay(animations, default_animation)

    def stop_display(self):
        if self._display is not None:
            self._display.close()
            self._display = None

    def change_face_animation(self, animation_name):
        if self._display is not None:
            self._display.change_animation(animation_name)

    # FACE DETECTION

    def start_face_detection(self, frequency=0.5, resize_factor=2, greet=False):
        if self._face_recognition is None:
            self._face_recognition = FaceRecognition(self._camera)
        self.face_recognition._resize_factor = resize_factor
        self._recognizer_frequency = frequency
        self._start_thread(self._recognizer_thread,
                           self._face_detection_loop,
                           'face_detection',
                           args=(greet,))

    def stop_face_detection(self):
        self._face_recognized = False
        self._running = False
        close_thread(self._recognizer_thread)

    def _face_detection_loop(self, greet=False):
        # process_this_frame = True
        # history_array_size = 2
        # history = [False] * history_array_size
        was_found = False
        # i = 0
        last_frame_time = 0
        while self._running:
            if time() - last_frame_time > self._recognizer_frequency:#process_this_frame:
                # print history
                self._face_recognized = self._face_recognition.haarcascade_face_detection()
                # history[i] = self._face_recognized
                #if True in history:
                if was_found or self._face_recognized:
                    self.change_face_animation('face_detected')
                    was_found = False
                else:
                    self.change_face_animation('idle')
                if self._face_recognized:
                    was_found = True
                self._move_arm_to_front() if greet else None
                last_frame_time = time()
                # i += 1
                # i = i % history_array_size
            # process_this_frame = not process_this_frame

    # GREETING

    def start_search(self, greet=True):
        from ..creatures.abstractcreature import actual_robot
        if not actual_robot:
            raise AttributeError('Intitialize a robot to use search behavior')
        self._search = True
        self._start_thread(self._greeting_thread,
                           self._search_loop,
                           'search',
                           args=(greet,),
                           force=True)

    def stop_search(self):
        self._search = False
        close_thread(self._greeting_thread)

    def _move_arm_to_front(self):
        if self._face_recognized:
            lado = actual_robot.head_z.present_position
            actual_robot.r_elbow_y.goto_position(0, 0.5, wait=True)
            actual_robot.r_arm_z.goto_position(lado, 1.0, wait=True)
            extended_since = time()
            print ('wait')
            while time() - extended_since < 2:
                if self._is_capacitive_enabled is not None:
                    while self._is_capacitive_enabled():
                        pass
            print ('fuera')
            actual_robot.r_arm_z.goto_position(0.0, 0.5, wait=True)
            actual_robot.r_elbow_y.goto_position(50.0, 1.0, wait=True)

    def _search_loop(self, greet):
        min_angle = -70
        max_angle = 70
        go_min = True
        go_max = False
        pos = 0
        amp = 2
        while self._search:
            if go_min and pos > min_angle:
                actual_robot.head_z.goto_position(pos, 0.5, wait=True)
                pos -= amp
            elif go_max and pos < max_angle:
                actual_robot.head_z.goto_position(pos, 0.5, wait=True)
                pos += amp
            else:
                go_min = not go_min
                go_max = not go_max
            self._move_arm_to_front() if greet else None

    # TRACKER

    def start_tracker(self, color, move_vertical=True):
        if not self._running:
            self._running = True
            self._tracker = Tracker(self._camera)
            self._tracker.move_vertical = move_vertical
            self._tracker.track_object_color(color)

    def stop_tracker(self, ):
        if self._tracker is not None:
            self._tracker.stop_tracker()
            self._tracker = None
            self._running = False

    # STOP THREADS

    def stop(self):
        self.stop_face_detection()
        self.stop_display()
        self.stop_search()
        self.stop_tracker()
