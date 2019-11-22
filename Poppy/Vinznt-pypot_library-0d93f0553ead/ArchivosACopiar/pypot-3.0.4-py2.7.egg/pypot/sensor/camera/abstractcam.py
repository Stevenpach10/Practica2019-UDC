import numpy as np
import cv2

from ...robot.sensor import Sensor

hsv_color_ranges = {
    "green": ([34, 50, 50], [80, 220, 200]),
    "red":  ([0, 50, 50], [20, 255, 255]),
    "yellow": ([20, 50, 50], [60, 255, 255])
}
default_gaussian_kernel_size = 9
default_threshold_limits = [10, 255]


class AbstractCamera(Sensor):
    registers = Sensor.registers + ['frame', 'resolution', 'fps']

    def __init__(self, name, resolution, fps):
        Sensor.__init__(self, name)

        self._res, self._fps = resolution, fps
        self._last_frame = self._grab_and_process()
        self._custom_filters = {}
        self.running = True
        self._contours_array_index = 1 if cv2.__version__.startswith("3.") else 0

    @property
    def frame(self):
        self._last_frame = self._grab_and_process()
        return self._last_frame

    def post_processing(self, image):
        return image

    def grab(self):
        raise NotImplementedError

    def _grab_and_process(self):
        return self.post_processing(self.grab())

    @property
    def resolution(self):
        return list(reversed(self.frame.shape[:2]))

    @property
    def fps(self):
        return self._fps

    def filter_objects_by_color_range(self, lower_hsv_range, upper_hsv_range):
        """Filter image objects between a given color range
        :param lower_hsv_range: lower color range in hsv format
        :param upper_hsv_range: upper color range in hsv format
        :return: filtered image array
        """
        image = self.frame
        if image is None:
            return None
        try:
            lower = np.array(lower_hsv_range, dtype=np.uint8)
            upper = np.array(upper_hsv_range, dtype=np.uint8)
            mask = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(mask, lower, upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            output = cv2.bitwise_and(image, image, mask=mask)
            return output
        except cv2.error:
            return None

    def _filter_by_predefined_color(self, color_tuple):
        lower, upper = color_tuple
        return self.filter_objects_by_color_range(lower, upper)

    def filter_red_objects(self):
        return self._filter_by_predefined_color(hsv_color_ranges["red"])

    def filter_green_objects(self):
        return self._filter_by_predefined_color(hsv_color_ranges["green"])

    def filter_yellow_objects(self):
        return self._filter_by_predefined_color(hsv_color_ranges["yellow"])

    def add_custom_filter(self, filter_name, custom_filter_function):
        """Add custom image filters to the camera class
        :param filter_name: The filter name
        :param custom_filter_function: filter function
        """
        self._custom_filters[filter_name] = custom_filter_function

    def run_custom_filter(self, name):
        """Executes previously added custom filters
        :param name: name of the added filter
        :return: Custom filter result. None if the filter name is not found
        """
        try:
            return self._custom_filters[name](self.grab())
        except KeyError:
            return None

    def get_image_objects(self, image, approximate=False, draw_contours=False, gaussian_filter_size=default_gaussian_kernel_size, threshold_limits=default_threshold_limits):
        # type: (list, bool, bool, int, [int,int]) -> (bool, list)
        """ Gets contour, center and area of objects found in image
        :param image: BGR image array
        :param approximate: to approximate the contour shape to another shape with less number of vertices
        :param draw_contours: to draw the contours and centers in the original image
        :param gaussian_filter_size: gaussian filter size odd number
        :param threshold_limits: list of two elements [lower limit, upper limit]
        :return: BGR image array, array of: (contour array, (x,y) element center, contour area)
        """

        if gaussian_filter_size % 2 == 0:
            gaussian_filter_size += 1

        if type(threshold_limits) == list:
            if len(threshold_limits) != 2:
                threshold_limits = default_threshold_limits
        else:
            threshold_limits = default_threshold_limits

        if image is None:
            return None, None

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_image, (gaussian_filter_size, gaussian_filter_size), 0)
        thresh = cv2.threshold(blurred, threshold_limits[0], threshold_limits[1], cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[self._contours_array_index]
        objects = []
        for contour in contours:
            if approximate:
                epsilon = 0.1 * cv2.arcLength(contour, True)
                contour = cv2.approxPolyDP(contour, epsilon, True)
            area = cv2.contourArea(contour)
            if area == 0:
                continue
            # compute the center of the contour
            M = cv2.moments(contour)
            try:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
                if draw_contours:
                    cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
                    cv2.circle(image, (center_x, center_y), 4, (255, 255, 255), -1)
                objects.append((contour, (center_x, center_y), area))
            except:
                pass
        return image, objects

    def close(self):
        self.running = False
