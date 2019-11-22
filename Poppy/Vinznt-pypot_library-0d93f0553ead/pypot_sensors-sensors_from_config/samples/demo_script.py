
from os.path import abspath
from pypot.creatures import PoppyTorso
config_path = abspath('./cam1.json')

poppy = PoppyTorso(config=config_path)

from pypot.extras.behavior_controller import BehaviorController
from pypot.sensor import ArduinoSensor

arduino = ArduinoSensor('arduino_pi', '/dev/ttyUSB0', 115200, False)
arduino.send_config_frequency_message(100)
hand_capacitive = lambda: arduino._receiver._capacitives[0] == 1

controller = BehaviorController(poppy.head_camera, get_capacitive_function=hand_capacitive, arduino=arduino)
animations = {'idle': '/home/poppy/videoPlayback/idle.gif',
              'face_detected': '/home/poppy/videoPlayback/found.gif'}


for m in poppy.motors:
    m.compliant = False
poppy.head_y.compliant = True

controller.start_display(animations, 'idle')


controller.start_face_recognition(0.4,1.1,False)
controller.start_search()

while True:
    pass