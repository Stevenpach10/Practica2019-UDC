# Make sure to have the server side running in V-REP: 
# in a child script of a V-REP scene, add following command
# to be executed just once, at simulation start:
#
# simRemoteApi.start(19999)
#
# then start simulation, and run this program.
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!


try:
    import vrep
except:
    print ('--------------------------------------------------------------')
    print ('"vrep.py" could not be imported. This means very probably that')
    print ('either "vrep.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time
import numpy as np
vrep.simxFinish(-1) # just in case, close all opened connections
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) # Connect to V-REP

def draw_VREP_Line(points):
    print(points)
    res = vrep.simxCallScriptFunction(clientID, 'Canvas', 
                                            vrep.sim_scripttype_childscript, 'draw_line', 
                                            [], points, [], bytearray(), vrep.simx_opmode_blocking)
    print(res)
print ('Program started')

if clientID!=-1:
    

    for i in range(500):
        print(i)
        np.random.normal()
        draw_VREP_Line([np.random.normal(),np.random.normal(),np.random.normal(),np.random.normal(),np.random.normal(),np.random.normal()])
else:
    print ('Failed connecting to remote API server')
print ('Program ended')
