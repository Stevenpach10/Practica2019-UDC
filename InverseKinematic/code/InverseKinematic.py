#****************************************************************************
#Image replication with the robotic device Poppy in a virtual simulator     *
#V-REP. Developed within the framework of the Professional Practice         *
#course-IC8842 of the bachelor's degree in Computer Engineering,            *
#Technological Institute of Costa Rica. With the support of the Integrated  *
#Engineering Group located on the Ferrol Campus of the University of Coruna *
#2019 Steven Andrey Pacheco Portuguez, Coruna, Espana                       *
#email stpacheco@ic-itcr.ac.cr                                              *
#****************************************************************************

import sys
from os.path import abspath
sys.path.append(abspath('./code/pix2seq'))
from sketch_pix2seq_sampling import getAbsoluteStrokes, drawAbsolutePosition
from collections import deque
from datetime import datetime
from skimage import color
from skimage import data
import pypot.vrep
import time
from pypot.sensor import OpenCVCamera
from pypot.creatures import PoppyTorso
import vrep
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from scripts import *
from util import *
import cv2

params = {}
fixes = 0


def getParams():
    params = {'vrep': True,                                                            # Indicates if we are using a simlator or not. True for use V-REP.
              'scene_path':  abspath('./vrep-sensors/torso_sensors_scene.ttt'),         # Path for V-REP's scene
              'config_path': abspath('./vrep-sensors/torso_vrep_sensors_config.json'),  # Path for Poppy's configuration in V-REP
              'config_path_sensor': abspath('./config/torso_config_cam01.json'),        # Path for Poppy's configuration sensor for real simulation
              'model_pix2seq_path': abspath('./code/pix2seq/outputs/snapshot'),         # Path Sketch model
              'path_image_target': abspath('./images/200.png'),                         # Path image source
              'image_predict_size': 0.10,                                               # Size of the image to draw by Poppy in centimeters
              'image_pixel_size': 48,                                                   # Pixel size from image source (Sketch image input size)
              'bounds': [-0.05, 0.05, 0.30],                                             # {x_bound_min, y_bound_min, bound_max} These parameters are used  drawing images limits.
              'rescale_factor': [1.10, 0.60],                                           # {x_factor, y_factor} These parameters are used for move the image in axis X and axis Y
                                                                                        # You can move the image result in the axis X and Y
              'drawing_speed': 0.2,                                                     # Drawing speed
              'acceptance_draw': [0.001, 0.001, 0.001],                                   # Error percentage allow while poppy is drawing. {X_error,Y_error,Z_error}
              'acceptance_without_draw': [0.1, 0.01, 0.1],                              # Error percentage allow while poppy is not drawing. {X_error,Y_error,Z_error}
              'Plane_Y': [-0.20, -0.17]                                                 # Plane Y where Poppy has to draw and when does not. {Y_draw, Y_Not_Draw}
              }
    return params
# *********************************************************************************************
# *                                                                                           *
# *                                   POPPY'S FUNCTION                                        *
# *                                                                                           *
# *                                                                                           *
# *********************************************************************************************

def getEffector(poppy):
    """Get the final effector from l_arm_chain of Poppy 

    Parameters
    -------------------
    poppy: PoppyTorso
        PoppyTorso instance

    Returns
    ------------------
    list
        a list with final position of effector (x,y,z) 
    """
    effector = poppy.l_arm_chain.end_effector
    return effector


def getDegrees(poppy):
    """Get the position joints from l_arm_chain of Poppy

    Parameters
    -------------------
    poppy: PoppyTorso
        PoppyTorso instance

    Returns
    ------------------
    single iterator object
         Motor's name and value of all chain
    """
    nameMotors = [motor.name for motor in poppy.l_arm_chain.motors]
    mapped = zip(nameMotors, poppy.l_arm_chain.joints_position)
    return mapped

def calc_difference(point, effector):
    """Compute the difference between a two points

    Parameters
    -------------------
    point: List
        Target point, three elements
    effector: List
        Actual point of effector, three elements

    Returns
    ------------------
    numpy list
        Absolute difference between point and effector in each axis 
    """
    result = [0, 0, 0]
    result[0] = abs(point[0]-effector[0])
    result[1] = abs(point[1]-effector[1])
    result[2] = abs(point[2]-effector[2])
    return result


def mov_head_get_image(poppy, vrep):
    """Turn the poppy's head to the right hand for capture an image and return

    Parameters
    -------------------
    poppy: PoppyTorso
        PoppyTorso instance
    vrep: Boolean
        Indicates if the image have to be obtain from V-REP or the real robot. True for V-REP

    Returns
    ------------------
    numpy list
        Image with default size  
    """
    poppy.head_y.goto_position(-20, 0.05)
    poppy.head_z.goto_position(-89, 0.05)
    time.sleep(2)
    if vrep:
        image = poppy.Vision_sensor.frame
    else:
        image = poppy.head_camera.frame
    time.sleep(2)
    poppy.head_y.goto_position(0, 0.05)
    poppy.head_z.goto_position(0, 0.05)
    return image

def mov_poppy_arm(chain, umbral, point):
    """Move a chain of Poppy to target point. While the difference between effector and end point
    is greater than the umbral. Move again the chain to reach the position.

    Parameters
    -------------------
    chain: IKChain
        Poppy's chain
    umbral: List
        The minimun error value allow for each axis (x, y, z)
    point: List
        Target point, three elements 

    Returns
    ------------------
    integer
        Iteration that had to do for reach the point
    """
    global fixes
    limit = 20
    iteration = 1
    chain.goto((point[0], point[1], point[2]),
               params['drawing_speed'], wait=True)

    effector = chain.end_effector
    diff = calc_difference(point, effector)
    while((diff[0] >= umbral[0] or diff[1] >= umbral[1] or diff[2] >= umbral[2]) and iteration <= limit):
        chain.goto((point[0], point[1], point[2]),
                   params['drawing_speed'], wait=True)
        time.sleep(0.1)
        effector = chain.end_effector
        diff = calc_difference(point, effector)
        fixes += 1
        iteration += 1
    return iteration


def init_pos(poppy,  compliant, time_sleep=0.5):
    """Set all Poppy's motor in a initial position and move the right hand.

    Parameters
    -------------------
    poppy: PoppyTorso
        PoppyTorso instance
    compliant: Boolean
        If compliant is True, the robot will go to turn off the motors. Else will move.
    time_sleep: Float, optional
        Time to wait between a motor to another
    """
    if compliant:
        for motor in poppy.motors:
            print(motor.name)
            motor.compliant = compliant
            time.sleep(time_sleep)
    else:
        for motor in poppy.motors:
            print(motor.name)
            motor.compliant = compliant
            motor.goto_position(0, 0.8)
            time.sleep(time_sleep)
        poppy.r_elbow_y.goto_position(90, 1)
        poppy.r_arm_z.goto_position(-45, 1)
        time.sleep(time_sleep)


def getInformation(position_draw_log, position_without_draw_log):
    """Get information about process drawing like mean, median, high value, low value and space of drawing 

    Parameters
    -------------------
    position_draw_log: list
        List of all position where poppy draw
    position_without_draw_log: list
        List of all position where poppy does not have to draw
    """
    y_draw = position_draw_log[:, 1]
    print("VALUES FOR PENCIL DRAWING")
    print("Low value : %.6f " % np.min(y_draw))
    print("Mean draw: %.6f " % np.mean(y_draw))
    print("Median draw: %.6f " % np.median(y_draw))
    print("High value : %.6f " % np.max(y_draw))
    print("Space of canvas  : %.6f " % (np.min(y_draw)-np.max(y_draw)))

    print("----------------------------------------------------------")
    print("VALUES FOR PENCIL WITHOUT DRAW")

    y_without_draw = position_without_draw_log[:, 1]
    print("Low value : %.6f " % np.min(y_without_draw))
    print("Mean without draw: %.6f " % np.mean(y_without_draw))
    print("Median draw: %.6f " % np.median(y_without_draw))
    print("High value : %.6f " % np.max(y_without_draw))
    print("Space of canvas  : %.6f " %
          (np.min(y_without_draw)-np.max(y_without_draw)))
# *********************************************************************************************
# *                                                                                           *
# *                                   POPPY'S FUNCTION DRAW                                   *
# *                                                                                           *
# *                                                                                           *
# *********************************************************************************************


def drawWithPoppyPointVREP(clientID, planeY, withoutDraw, strokes, poppy, umbral, umbral_without):
    """Draw points according all strokes in a simulation environment

    Parameters
    -------------------
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.
    planeY: Float
        Value of the axis Y that poppy has to draw. In meters
    withoutDraw: Float
        Value of the axis Y that poppy has not to draw. In meters
    strokes: List
        List of all strokes that poppy has to draw
    poppy: PoppyTorso
        PoppyTorso instance
    umbral: List
        The minimun error value allow for each axis, when poppy draw (x, y, z)
    umbral: List
        The minimun error value allow for each axis, when poppy does not draw (x, y, z)
    Returns
    ------------------
    List
        Return three list. One with all points that poppy reach. 
        The other is all points that draw
        The last one is all points when poppy doesn't have to draw
    """
    axisY = planeY
    stroke_i = 0
    umbralR = (0, 0, 0)
    size = len(strokes)
    position_draw_log = []
    position_without_draw_log = []
    position_total = []
    auxhandle = vrep.simxGetObjectHandle(
        clientID, 'l_ball', vrep.simx_opmode_blocking)
    position = vrep.simxGetObjectPosition(
        clientID, auxhandle[1], -1, vrep.simx_opmode_streaming)
    start = datetime.now()
    for stroke in strokes:
        if stroke[2] == 0:
            axisY = planeY
            umbralR = umbral
        else:
            axisY = withoutDraw
            umbralR = umbral_without
        i = mov_poppy_arm(poppy.l_arm_chain, umbralR,
                          (stroke[0], axisY, stroke[1]))
        stroke_i += 1
        position = vrep.simxGetObjectPosition(
            clientID, auxhandle[1], -1, vrep.simx_opmode_buffer)
        if(axisY == planeY):
            position_draw_log.append(position[1])
            draw_VREP_Point([position[1][0], position[1][1] -
                             0.04, position[1][2]], clientID)
        else:
            position_without_draw_log.append(position[1])
        position_total.append(position[1])
        print("Move %.d" % stroke_i + " from %.d" %
              size + " iterations to converge : %.d" % i)
    end = datetime.now()
    print("-----------------------------------------------")
    print(diff_time(start, end))
    mov_poppy_arm(poppy.l_arm_chain, umbral,
                  (stroke[0], withoutDraw, stroke[1]))
    return position_total, position_draw_log, position_without_draw_log


def draw_line(queue, clientID):
    """ Draw a line in the simulator V-REP using two points. 

    Parameters
    -------------------
    queue: List
        List with two points, each point is an array with three elements. 
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.

    Returns
    ------------------
    List
        If function end correctly return a empty list. If not return the 
        input list.
    """
    if(len(queue) != 2):
        return queue
    initial_point = queue.popleft()
    final_point = queue.popleft()
    line = np.asarray([initial_point, final_point]).flatten()
    draw_VREP_Line(line, clientID)
    return queue


def drawWithPoppyLineVREP(clientID, planeY, withoutDraw, strokes, poppy, umbral, umbral_without):
    """Draw lines according all strokes in a simulation environment

    Parameters
    -------------------
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.
    planeY: Float
        Value of the axis Y that poppy has to draw. In meters
    withoutDraw: Float
        Value of the axis Y that poppy has not to draw. In meters
    strokes: List
        List of all strokes that poppy has to draw
    poppy: PoppyTorso
        PoppyTorso instance
    umbral: List
        The minimun error value allow for each axis, when poppy draw (x, y, z)
    umbral: List
        The minimun error value allow for each axis, when poppy does not draw (x, y, z)
    Returns
    ------------------
    List
        Return three list. One with all points that poppy reach. 
        The other is all points that draw
        The last one is all points when poppy doesn't have to draw
    """
    axisY = planeY
    stroke_i = 0
    line = deque()
    umbralR = (0, 0, 0)
    size = len(strokes)
    position_draw_log = []
    position_without_draw_log = []
    position_total = []
    auxhandle = vrep.simxGetObjectHandle(
        clientID, 'l_ball', vrep.simx_opmode_blocking)
    position = vrep.simxGetObjectPosition(
        clientID, auxhandle[1], -1, vrep.simx_opmode_streaming)
    start = datetime.now()
    for stroke in strokes:
        if stroke[2] == 0:
            axisY = planeY
            umbralR = umbral
        else:
            axisY = withoutDraw
            umbralR = umbral_without

        i = mov_poppy_arm(poppy.l_arm_chain, umbralR,
                          (stroke[0], axisY, stroke[1]))
        stroke_i += 1
        position = vrep.simxGetObjectPosition(
            clientID, auxhandle[1], -1, vrep.simx_opmode_buffer)
        if(axisY == planeY):
            position_draw_log.append(position[1])
            line.append([position[1][0], position[1][1], position[1][2]])
            if (len(line) == 2):
                draw_line(line, clientID)
                line.append([position[1][0], position[1][1], position[1][2]])
        else:
            if(len(line) == 1):
                line.popleft()
            position_without_draw_log.append(position[1])
        position_total.append(position[1])
        print("Move %.d" % stroke_i + " from %.d" %
              size + " iterations to converge : %.d" % i)
    end = datetime.now()
    print("-----------------------------------------------")
    print(diff_time(start, end))
    mov_poppy_arm(poppy.l_arm_chain, umbral, (0.01, -0.15, 0.10))
    return position_total, position_draw_log, position_without_draw_log


def drawWithPoppyLine(planeY, withoutDraw, strokes, poppy, umbral, umbral_without):
    """Draw lines according all strokes with real poppy robot

    Parameters
    -------------------
    planeY: Float
        Value of the axis Y that poppy has to draw. In meters
    withoutDraw: Float
        Value of the axis Y that poppy has not to draw. In meters
    strokes: List
        List of all strokes that poppy has to draw
    poppy: PoppyTorso
        PoppyTorso instance
    umbral: List
        The minimun error value allow for each axis, when poppy draw (x, y, z)
    umbral: List
        The minimun error value allow for each axis, when poppy does not draw (x, y, z)
    Returns
    ------------------
    List
        Return three list. One with all points that poppy reach. 
        The other is all points that draw
        The last one is all points when poppy doesn't have to draw
    """
    axisY = planeY
    stroke_i = 0
    umbralR = (0, 0, 0)
    size = len(strokes)
    position_draw_log = []
    position_without_draw_log = []
    position_total = []

    start = datetime.now()
    for stroke in strokes:
        if stroke[2] == 0:
            axisY = planeY
            umbralR = umbral
        else:
            axisY = withoutDraw
            umbralR = umbral_without

        i = mov_poppy_arm(poppy.l_arm_chain, umbralR,
                          (stroke[0], axisY, stroke[1]))

        position = getEffector(poppy)
        stroke_i += 1
        if(axisY == planeY):
            position_draw_log.append(position)
        else:
            position_without_draw_log.append(position)
        position_total.append(position)
        print("Move %.d" % stroke_i + " from %.d" %
              size + " iterations to converge : %.d" % i)
    end = datetime.now()
    print("-----------------------------------------------")
    print(diff_time(start, end))
    return position_total, position_draw_log, position_without_draw_log


def getImagePoppy(poppy, vrep):
    """Get the image from camera and transform for be consumed by Sketch-pix2seq

    Parameters
    -------------------
    poppy: PoppyTorso
        PoppyTorso instance
    vrep: Boolean
        Indicates if the image have to be obtain from V-REP or the real robot. True for V-REP

    Returns
    ------------------
    list
        The image with the right shape (1, 48, 48, 1)
    """
    image = mov_head_get_image(poppy, vrep)
    image = cv2.resize(image, (48, 48), interpolation=cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = np.reshape(image, (1, 48, 48, 1))
    return image


def main():
    global params
    params = getParams()

    if(params['vrep']):
        vrep.simxFinish(-1)
        print(params['config_path'])
        poppy = PoppyTorso(
            simulator='vrep', scene=params['scene_path'], config=params['config_path'])
        clientID = vrep.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
        add_texture_TV(params['path_image_target'], clientID)

        image = getImagePoppy(poppy, params['vrep'])
        strokes = getAbsoluteStrokes(
            '', '', params["model_pix2seq_path"], image)
        stroke_rescale = rescaledImage(
            strokes, params['image_pixel_size'], params['image_predict_size'], params["rescale_factor"][0], params["rescale_factor"][1])
        drawAbsolutePosition(stroke_rescale, (params['bounds'][0], params['bounds'][0]+params['bounds'][2],
                                              params['bounds'][1], params['bounds'][1]+params['bounds'][2]))

        position_total, position_draw_log, position_without_draw_log = drawWithPoppyLineVREP(clientID, params['Plane_Y'][0], params['Plane_Y'][1],
                                                                                             stroke_rescale, poppy, params['acceptance_draw'], params['acceptance_without_draw'])
        vrep.simxFinish(clientID)
    else:
        poppy = PoppyTorso(config=params['config_path'])
        init_pos(poppy, False, 0.1)
        image = getImagePoppy(poppy, params['vrep'])
        strokes = getAbsoluteStrokes(
            '', '', params["model_pix2seq_path"], image)
        stroke_rescale = rescaledImage(
            strokes, params['image_pixel_size'], params['image_predict_size'], params["rescale_factor"][0], params["rescale_factor"][1])
        drawAbsolutePosition(stroke_rescale, (params['bounds'][0], params['bounds'][0]+params['bounds'][2],
                                              params['bounds'][1], params['bounds'][1]+params['bounds'][2]))

        position_total, position_draw_log, position_without_draw_log = drawWithPoppyLine(params['Plane_Y'][0], params['Plane_Y'][1],
                                                                                         stroke_rescale, poppy, params['acceptance_draw'], params['acceptance_without_draw'])

        init_pos(poppy, False, 0.1)

    position_draw_log = np.asarray(position_draw_log)
    position_without_draw_log = np.asarray(position_without_draw_log)
    position_total = np.asarray(position_total)

    plotAllData(position_total)


if __name__ == '__main__' and __package__ is None:
    __package__ = 'pix2seq'
    main()
