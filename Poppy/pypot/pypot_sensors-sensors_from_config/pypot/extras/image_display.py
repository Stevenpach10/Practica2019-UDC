import cv2
import imageio
from os.path import splitext
from threading import Thread
from time import time

gif_animations = {}
gif_sizes = {}


class ImageDisplay(object):
    def __init__(self, animations, default_animation, fps=15):
        if not animations:
            raise AttributeError('No animations specified')
        if default_animation not in animations:
            raise AttributeError("Default animation '{}' doesn't exists in animations".format(default_animation))
        self.animations = animations
        self._window_name = 'faceDisplay'
        self._actual_animation = None
        self._actual_animation_name = None
        self._gif_frame_number = 0
        self._display_thread = None
        self._display_function = None
        self._gif_to_frames()
        self.change_animation(default_animation)
        self._running = False
        self._frame_frequency = 1.0 / fps
        self._last_display_time = 1
        self.start()

    @property
    def fps(self):
        return 1.0/self._frame_frequency

    @fps.setter
    def fps(self, value):
        self._frame_frequency = 1.0/value

    def _gif_to_frames(self):
        for animation_name in self.animations:
            animation_path = self.animations[animation_name]
            filename, file_extension = splitext(animation_path)
            if file_extension == '.gif':
                gif_frames = imageio.mimread(animation_path)
                gif_size = len(gif_frames)
                if gif_size > 0:
                    bgr_frames = [cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) for frame in gif_frames]
                    gif_animations[animation_name] = bgr_frames
                    gif_sizes[animation_name] = gif_size
                else:
                    raise ImportError("Can't open {} gif".format(self.animations[animation_name]))

    def start(self):
        if self._display_thread is None:
            self._window_name = '{}1'.format(self._window_name)
            self._display_thread = Thread(target=self._display_loop)
            self._display_thread.daemon = True
            self._running = True
            self._display_thread.start()

    def _load_animation(self, animation_name):
        animation_path = self.animations[animation_name]
        filename, file_extension = splitext(animation_path)
        if file_extension == '.gif':
            if animation_name in gif_animations:
                return gif_animations[animation_name], self._display_gif
        else:
            video = cv2.VideoCapture(self.animations[animation_name])
            if video.isOpened():
                return video, self._display_video
            else:
                raise ImportError("Can't open {} video".format(self.animations[animation_name]))

    def change_animation(self, animation_name):
        if self._actual_animation_name != animation_name:
            if animation_name in self.animations:
                self._actual_animation, self._display_function = self._load_animation(animation_name)
                self._gif_frame_number = 0
                self._actual_animation_name = animation_name

    def _display_video(self):
        if self._actual_animation.isOpened():
            ret, frame = self._actual_animation.read()
            if ret:
                cv2.imshow(self._window_name, frame)
            else:
                self._actual_animation.set(cv2.CAP_PROP_POS_FRAMES, 1)
            cv2.waitKey(1)

    def _display_gif(self):
        if self._gif_frame_number < gif_sizes[self._actual_animation_name]:
            cv2.imshow(self._window_name, self._actual_animation[self._gif_frame_number])
            cv2.waitKey(1)
            self._gif_frame_number += 1
        else:
            self._gif_frame_number = 0

    def _display_loop(self):
        cv2.namedWindow(self._window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self._window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.waitKey(1)
        while self._running:
            if time() - self._last_display_time > self._frame_frequency:
                self._display_function()
                self._last_display_time = time()

    def close(self):
        self._running = False
        self._display_thread.join()
        self._display_thread = None
        print ('fin')
        cv2.destroyWindow(self._window_name)
