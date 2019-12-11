import vrep

def draw_VREP_Point(points, clientID):
    res = vrep.simxCallScriptFunction(clientID, 'Canvas', 
                                                vrep.sim_scripttype_childscript, 'draw_point', 
                                                [], points, [], bytearray(), vrep.simx_opmode_blocking)
    return res
def draw_VREP_Line(points, clientID):
    res = vrep.simxCallScriptFunction(clientID, 'Canvas', 
                                            vrep.sim_scripttype_childscript, 'draw_line', 
                                            [], points, [], bytearray(), vrep.simx_opmode_blocking)
    return res
def add_texture_TV(path, clientID):
    res = vrep.simxCallScriptFunction(clientID, 'Image', 
                                                vrep.sim_scripttype_childscript, 'add_texture', 
                                                [], [], [], path, vrep.simx_opmode_blocking)
    print(res)