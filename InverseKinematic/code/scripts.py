#****************************************************************************
#Image replication with the robotic device Poppy in a virtual simulator     *
#V-REP. Developed within the framework of the Professional Practice         *
#course-IC8842 of the bachelor's degree in Computer Engineering,            *
#Technological Institute of Costa Rica. With the support of the Integrated  *
#Engineering Group located on the Ferrol Campus of the University of Coruna *
#2019 Steven Andrey Pacheco Portuguez, Coruna, Espana                       *
#email stpacheco@ic-itcr.ac.cr                                              *
#****************************************************************************
import vrep

def draw_VREP_Point(points, clientID):
    """Allow draw point in V-REP through vrep API calling a script function in a scene 

    Parameters
    -------------------
    point: List
        List with two points, each point with the shape (1,3)
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.

    Returns
    ------------------
    list
        list with response of script in VREP 
    """
    res = vrep.simxCallScriptFunction(clientID, 'Canvas', 
                                                vrep.sim_scripttype_childscript, 'draw_point', 
                                                [], points, [], bytearray(), vrep.simx_opmode_blocking)
    return res

def draw_VREP_Line_Red(points, clientID):
    """Allow draw a line red in V-REP through vrep API calling a script function in a scene 

    Parameters
    -------------------
    point: List
        List with two points, each point with the shape (1,3)
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.

    Returns
    ------------------
    list
        list with response of script in VREP 
    """
    res = vrep.simxCallScriptFunction(clientID, 'Canvas', 
                                            vrep.sim_scripttype_childscript, 'draw_line2', 
                                            [], points, [], bytearray(), vrep.simx_opmode_blocking)
    return res

def draw_VREP_Line(points, clientID):
    """Allow draw a line yellow in V-REP through vrep API calling a script function in a scene 

    Parameters
    -------------------
    point: List
        List with two points, each point with the shape (1,3)
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.

    Returns
    ------------------
    list
        list with response of script in VREP 
    """
    res = vrep.simxCallScriptFunction(clientID, 'Canvas', 
                                            vrep.sim_scripttype_childscript, 'draw_line', 
                                            [], points, [], bytearray(), vrep.simx_opmode_blocking)
    return res
def add_texture_TV(path, clientID):
    """Allow add texture to simulator TV. 

    Parameters
    -------------------
    path: String
        string with the path of the texture to load.
    clientID: Integer
        Identifier of the connection with V-REP scene simulation.

    Returns
    ------------------
    list
        list with response of script in VREP 
    """
    res = vrep.simxCallScriptFunction(clientID, 'Image', 
                                                vrep.sim_scripttype_childscript, 'add_texture', 
                                                [], [], [], path, vrep.simx_opmode_blocking)
    print(res)