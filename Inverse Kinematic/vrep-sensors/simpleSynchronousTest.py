# This small example illustrates how to use the remote API
# synchronous mode. The synchronous mode needs to be
# pre-enabled on the server side. You would do this by
# starting the server (e.g. in a child script) with:
#
# simRemoteApi.start(19999,1300,false,true)
#
# But in this example we try to connect on port
# 19997 where there should be a continuous remote API
# server service already running and pre-enabled for
# synchronous mode.
#
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!

try:
    from pypot.vrep import remote_api,vrep_session_id
except:
    print ('--------------------------------------------------------------')
    print ('"vrep.py" could not be imported. This means very probably that')
    print ('either "vrep.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time
import sys

print ('Program started')
remote_api.simxFinish(-1) # just in case, close all opened connections
clientID=remote_api.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to V-REP
if clientID!=-1:
    print ('Connected to remote API server')

    # enable the synchronous mode on the client:
    remote_api.simxSynchronous(clientID,True)

    # start the simulation:
    remote_api.simxStartSimulation(clientID,remote_api.simx_opmode_blocking)

    # Now step a few times:
    for i in range(0, 15):
        remote_api.simxSynchronousTrigger(clientID)

    posicin = remote_api.simxCallScriptFunction(clientID, 'Sphere', remote_api.sim_scripttype_childscript, 'valores', [], [], [], bytearray(), vrep.simx_opmode_blocking)

    print(posicin)
    # stop the simulation:
    remote_api.simxStopSimulation(clientID,remote_api.simx_opmode_blocking)
    remote_api.simxFinish(clientID)
else:
    print ('Failed connecting to remote API server')
print ('Program ended')
