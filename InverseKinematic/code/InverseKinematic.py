
import cv2
from util import *
from scripts import *
import ikpy
import sys
import matplotlib.pyplot as plt
import vrep
from ikpy import plot_utils
from os.path import abspath
from pypot.creatures import PoppyTorso
from pypot.sensor import OpenCVCamera
import time
from pypot.vrep import remote_api,vrep_session_id
from skimage import data, color
from datetime import datetime
from collections import deque
sys.path.append('./code/pix2seq')
from sketch_pix2seq_sampling import getAbsoluteStrokes,drawAbsolutePosition
def getParams():
    params = {'vrep': True,
              'scene_path' :  abspath('./vrep-sensors/torso_sensors_scene.ttt'),           #Path for V-REP's scene 
              'config_path' : abspath('./vrep-sensors/torso_vrep_sensors_config.json'),    #Path for Poppy's configuration in V-REP
              'config_path_sensor' : abspath('./config/torso_config_cam01.json'),          #Path for Poppy's configuration sensor for real simulation
              'model_pix2seq_path' : abspath('./code/pix2seq/outputs/snapshot'),           #Path Sketch model
              'path_image_target' : abspath('./images/194.png'),                           #Path image source
              'image_predict_size' : 0.15,                                                 #Size of the image to draw by Poppy in centimeters
              'image_pixel_size' : 48,                                                     #Pixel size from image source (Sketch image input size)
              'bounds' : [-0.15,0.10,0.30],                                                #{x_bound_min, y_bound_min, bound_max} These parameters are used  drawing images limits.
              'rescale_factor' : [1.12, 0.72],                                             #{x_factor, y_factor} These parameters are used for move the image in axis X and axis Y
                                                                                           #You can move the image result in the axis X and Y
              'acceptance_draw' : [0.002, 0.002, 0.002],                                   #Error percentage allow while poppy is drawing. {X_error,Y_error,Z_error}
              'acceptance_without_draw' : [0.1, 0.01, 0.1],                                #Error percentage allow while poppy is not drawing. {X_error,Y_error,Z_error}
              'Plane_Y' : [-0.24, -0.13]                                                   #Plane Y where Poppy has to draw and when does not. {Y_draw, Y_Not_Draw}
                }
    return params
#*********************************************************************************************
#*                                                                                           *
#*                                   POPPY'S FUNCTION                                        *
#*                                                                                           *
#*                                                                                           *
#*********************************************************************************************

def getEffector(poppy):
    effector = poppy.l_arm_chain.end_effector
    print("X : %.6f" % effector[0] + ", Y : %.6f" % effector[1] + ", Z : %.6f" % effector[2])
    return effector

def getDegrees(poppy):
    nameMotors = [motor.name for motor in poppy.l_arm_chain.motors]
    mapped = zip(nameMotors, poppy.l_arm_chain.joints_position)
    return mapped

def getPicture(poppy):
    return poppy.Vision_sensor.frame

def calc_difference(point,effector):
    result = [0,0,0]
    result[0] = abs(point[0]-effector[0])
    result[1] = abs(point[1]-effector[1])
    result[2] = abs(point[2]-effector[2])
    return result

def mov_head_get_image(poppy):
    poppy.head_y.goto_position(-16,0.05)
    poppy.head_z.goto_position(-88,0.05)
    time.sleep(1)
    image = getPicture(poppy)
    time.sleep(1)
    poppy.head_y.goto_position(0,0.05)
    poppy.head_z.goto_position(0,0.05)
    return image

def mov_poppy_arm(chain, umbral, point):
    iteration = 1
    effector = chain.end_effector
    diff = calc_difference(point, effector)
    while((diff[0] >= umbral[0] or diff[1] >= umbral[1] or diff[2] >= umbral[2]) and iteration <= 50):
        chain.goto((point[0], point[1], point[2]), 0.1, wait=True)
        time.sleep(0.1)
        effector = chain.end_effector
        diff = calc_difference(point, effector)
        iteration += 1
    return iteration

def getInformation(position_draw_log, position_without_draw_log):
    y_draw = position_draw_log[:,1]
    print("VALUES FOR PENCIL DRAWING")
    print("Low value : %.6f " % np.min(y_draw))
    print("Mean draw: %.6f " % np.mean(y_draw))
    print("Median draw: %.6f " % np.median(y_draw))
    print("High value : %.6f " % np.max(y_draw))
    print("Space of canvas  : %.6f " % (np.min(y_draw)-np.max(y_draw)))

    print("----------------------------------------------------------")
    print("VALUES FOR PENCIL WITHOUT DRAW")

    y_without_draw = position_without_draw_log[:,1]
    print("Low value : %.6f " % np.min(y_without_draw))
    print("Mean without draw: %.6f " % np.mean(y_without_draw))
    print("Median draw: %.6f " % np.median(y_without_draw))
    print("High value : %.6f " % np.max(y_without_draw))
    print("Space of canvas  : %.6f " % (np.min(y_without_draw)-np.max(y_without_draw)))
#*********************************************************************************************
#*                                                                                           *
#*                                   POPPY'S FUNCTION DRAW                                   *
#*                                                                                           *
#*                                                                                           *
#*********************************************************************************************    
#  
def drawWithPoppyPoint(clientID, planeY, withoutDraw, strokes, poppy, umbral, umbral_without):
    axisY = planeY
    stroke_i = 0
    umbralR = (0, 0, 0)
    size = len(strokes)
    position_draw_log = []
    position_without_draw_log = []
    position_total = []
    auxhandle = vrep.simxGetObjectHandle(clientID, 'l_ball', vrep.simx_opmode_blocking)
    position = vrep.simxGetObjectPosition(clientID, auxhandle[1], -1, vrep.simx_opmode_streaming)
    start = datetime.now()
    for stroke in strokes:
        if stroke[2] == 0:
            axisY = planeY
            umbralR = umbral
        else:
            axisY = withoutDraw
            umbralR = umbral_without
        i = mov_poppy_arm(poppy.l_arm_chain, umbralR, (stroke[0], axisY, stroke[1]))
        stroke_i += 1
        position = vrep.simxGetObjectPosition(clientID, auxhandle[1], -1, vrep.simx_opmode_buffer)
        if(axisY == planeY):
            position_draw_log.append(position[1])
            draw_VREP_Point([position[1][0],position[1][1]-0.04,position[1][2]], clientID)
        else:
            position_without_draw_log.append(position[1])
        position_total.append(position[1])
        print("Move %.d" % stroke_i + " from %.d" % size + " iterations to converge : %.d" % i)
    end = datetime.now()
    print("-----------------------------------------------")
    print(diff_time(start, end))
    mov_poppy_arm(poppy.l_arm_chain, umbral, (stroke[0], withoutDraw, stroke[1]))
    return position_total, position_draw_log, position_without_draw_log

def draw_line(queue, clientID):
    if(len(queue) != 2):
        return queue
    initial_point = queue.popleft()
    final_point = queue.popleft()
    line = np.asarray([initial_point,final_point]).flatten()
    draw_VREP_Line(line, clientID)
    return queue

def drawWithPoppyLine(clientID, planeY, withoutDraw, strokes, poppy, umbral, umbral_without):
    axisY = planeY
    stroke_i = 0
    line = deque()
    umbralR = (0, 0, 0)
    size = len(strokes)
    position_draw_log = []
    position_without_draw_log = []
    position_total = []
    auxhandle = vrep.simxGetObjectHandle(clientID, 'l_ball', vrep.simx_opmode_blocking)
    position = vrep.simxGetObjectPosition(clientID, auxhandle[1], -1, vrep.simx_opmode_streaming)
    start = datetime.now()
    for stroke in strokes:
        if stroke[2] == 0:
            axisY = planeY
            umbralR = umbral
        else:
            axisY = withoutDraw
            umbralR = umbral_without
        
        i = mov_poppy_arm(poppy.l_arm_chain, umbralR, (stroke[0], axisY, stroke[1]))
        stroke_i += 1
        position = vrep.simxGetObjectPosition(clientID, auxhandle[1], -1, vrep.simx_opmode_buffer)
        if(axisY == planeY):
            position_draw_log.append(position[1])
            line.append([position[1][0],position[1][1],position[1][2]])
            if (len(line) == 2):
                draw_line(line, clientID)
                line.append([position[1][0],position[1][1],position[1][2]])
        else:
            if(len(line) == 1):
                line.popleft()
            position_without_draw_log.append(position[1])
        position_total.append(position[1])
        print("Move %.d" % stroke_i + " from %.d" % size + " iterations to converge : %.d" % i)
    end = datetime.now()
    print("-----------------------------------------------")
    print(diff_time(start, end))
    mov_poppy_arm(poppy.l_arm_chain, umbral, (0.01, -0.15, 0.10))
    return position_total, position_draw_log, position_without_draw_log      



def main():
    from pypot.vrep import remote_api,vrep_session_id
    
    params = getParams()
    vrep.simxFinish(-1)
    if(params['vrep']):
        poppy = PoppyTorso(simulator='vrep', scene=params['scene_path'], config=params['config_path'])
    else:
        poppy = PoppyTorso(config=params['config_path_sensors'])
        for motor in poppy.motors:
            motor.compliant = True
            motor.goto_position(0, 3)

        poppy.bust_y.compliant = True
        poppy.r_elbow_y.goto_position(10.9,0.5)
        poppy.r_arm_z.goto_position(-45,0.5) 

    clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)
    add_texture_TV(params['path_image_target'],clientID)
    image = mov_head_get_image(poppy)

    image = cv2.resize(image,(48,48), interpolation = cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(image.shape)
    print("**********************RESHAPE**************************")
    image = np.reshape(image,(1,48,48,1))
    #plt.imshow(image,cmap='gray', vmin=0, vmax=255)
    
    strokes = getAbsoluteStrokes('','',params["model_pix2seq_path"],image)
    
    stroke_rescale = rescaleImage(strokes, params['image_pixel_size'], params['image_predict_size'],params["rescale_factor"][0], params["rescale_factor"][1])
    drawAbsolutePosition(stroke_rescale,(params['bounds'][0],params['bounds'][0]+params['bounds'][2],
                            params['bounds'][1], params['bounds'][1]+params['bounds'][2]))
    
    position_total, position_draw_log, position_without_draw_log  = drawWithPoppyLine(clientID, params['Plane_Y'][0], params['Plane_Y'][1] ,
             stroke_rescale, poppy, params['acceptance_draw'], params['acceptance_without_draw'])

    position_draw_log = np.asarray(position_draw_log)
    position_without_draw_log = np.asarray(position_without_draw_log)
    position_total = np.asarray(position_total)
    vrep.simxFinish(clientID)

    plotAllData(position_total)
    
if __name__ == '__main__' and __package__ is None:
    __package__ = 'pix2seq'
    main()