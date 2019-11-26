import requests
import json
from threading import Thread


class Imitator(object):
    def __init__(self, remote_robots=[], local_robots=[]):
        self._local_robots = local_robots
        self._remote_robots = remote_robots
        self._responses = []
        self._finished_requests_counter = 0

    @property
    def local_robots(self):
        return self._local_robots

    @property
    def remote_robots(self):
        return self._remote_robots

    def _get_local_response(self, robot, command, get_value, array_position):
        formatted_command = '{}.{}'.format(robot, command)
        try:
            if get_value:
                self._responses[array_position] = {'result': eval(formatted_command)}
            else:
                exec formatted_command
                self._responses[array_position] = {'result': None}
        except Exception as error:
            self._responses[array_position] = {'error': error}
        self._finished_requests_counter += 1

    def _get_remote_response(self, ip_and_port, payload, array_position):
        try:
            request = requests.post('http://{}/run_instruction'.format(ip_and_port),
                                    data=json.dumps(payload),
                                    headers={'content-type': 'application/json'},
                                    timeout=5)
            response = request.json()
            self._responses[array_position] = response
        except requests.exceptions.ConnectionError as error:
            self._responses[array_position] = {'error': error}
        self._finished_requests_counter += 1

    def imitate(self, command, get_value=True):
        local_robots_array_length = len(self._local_robots)
        expected_responses = len(self._remote_robots) + local_robots_array_length
        self._responses = [{'error': 'No response'}] * expected_responses
        self._finished_requests_counter = 0
        robot_counter = 0

        for robot_ip_and_port in self._remote_robots:
            request_body = {'instruction': command, 'get': get_value}
            Thread(name=robot_ip_and_port,
                   target=self._get_remote_response,
                   args=(robot_ip_and_port, request_body, robot_counter,)
                   ).start()
            robot_counter += 1

        for local_robot_pos in range(0, local_robots_array_length):
            Thread(name='local_robot_{}'.format(local_robot_pos),
                   target=self._get_local_response,
                   args=('self._local_robots[{}]'.format(local_robot_pos),
                         command,
                         get_value,
                         robot_counter,)).start()
            robot_counter += 1

        while self._finished_requests_counter < expected_responses:
            pass

        return self._responses
