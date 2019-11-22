from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import numpy as np
import random as rd
import time
from cv2 import *
from matplotlib.patches import FancyArrowPatch
from matplotlib import patches
from mpl_toolkits.mplot3d import proj3d

# Distancias en mm
xz01_low_limit = 25     # Distancias en mm
xz01_upp_limit = 175    # Distancias en mm
y01_low_limit = 50      # Distancias en mm
y01_upp_limit = 150     # Distancias en mm

# Distancias en mm
xz02_low_limit = -25    # Distancias en mm
xz02_upp_limit = 225    # Distancias en mm
y02_low_limit = 50      # Distancias en mm
y02_upp_limit = 225     # Distancias en mm

# Distancias en mm
xz03_low_limit = -100   # Distancias en mm
xz03_upp_limit = 350    # Distancias en mm
y03_low_limit = 50      # Distancias en mm
y03_upp_limit = 350     # Distancias en mm

# -----------------------  Funcion para representar vectores en 3D  ----------------------------------------------------
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)
# ----------------------------------------------------------------------------------------------------------------------


# ---------------------  Matrix transformation from the relative system to the absolute system  ------------------------
def buildTransformationMatrix(long1, long2, angle1, angle2):

    aux = np.ones((4,4))
    aux[0][0] = np.cos(angle2)                      # r11 = np.cos(beta)
    aux[0][1] = 0.0                                 # r12 = 0
    aux[0][2] = np.sin(angle2)                      # r13 = np.sin(beta)
    aux[0][3] = 0.0                                 # lamb1 = 0
    aux[1][0] = 0.0                                 # r21 = 0
    aux[1][1] = 1.0                                 # r22 = 1
    aux[1][2] = 0.0                                 # r23 = 0
    aux[1][3] = (long1 + long2) * np.cos(angle1)    # lamb2 = (l1 + l2) * np.cos(alfa)
    aux[2][0] = -np.sin(angle2)                     # r31 = -np.sin(beta)
    aux[2][1] = 0.0                                 # r32 = 0
    aux[2][2] = np.cos(angle2)                      # r33 = np.cos(beta)
    aux[2][3] = (long1 + long2) * np.sin(angle1)    # lamb3 = (l1 + l2) * np.sin(alfa)
    aux[3][0] = 0.0
    aux[3][1] = 0.0
    aux[3][2] = 0.0
    aux[3][3] = 1.0

    return aux
# ----------------------------------------------------------------------------------------------------------------------


# ------------------  Funcion para representar los valores del fitness de las diferentes generaciones  -----------------
def drawDistanceParameters(sac_medias, s_final_media, s_acento, s_final, gen):

    x = [n for n in range(0, len(s_acento))]
    top_limit = int(max(sac_medias))
    z_up = [n for n in range(0, top_limit)]

    """
    first_step = [first_trigger for n in range(0, top_limit)]
    second_step = [second_trigger for n in range(0, top_limit)]

    plt.plot(first_step, z_up, color = 'r', linestyle = 'dashed')
    plt.plot(second_step, z_up, color='r', linestyle='dashed')
    """

    fig, ax = plt.subplots()

    ax.set_title('(noStaged) Distancias varias del mejor individuo en cada generacion')
    ax.set_ylabel('Valor distancia en (cm)')
    ax.set_xlabel('Numero de generaciones')

    plt.plot(x, s_acento, color = 'r', label ='Mejor Suma trayectorias')
    plt.plot(x, s_final, color = 'c', label ='Mejor Final')
    plt.plot(x, sac_medias, color = 'g', label ='Media Trayectorias')
    plt.plot(x, s_final_media, color='y', label='Media dist. Final')
    plt.xlim([0.0, gen - 1])
    plt.ylim([0.0, 500.0])
    plt.legend()
    aux_01 = time.strftime("%Y_%m_%d__imagenTrayectorias")
    aux02 = aux_01 + 'jpg'
    plt.savefig(aux02)
    plt.show()
    plt.close()
# ----------------------------------------------------------------------------------------------------------------------


# -------------------  Set the position of the point, referenced to the relative coordinate system  --------------------
def point2ndSystem (lon, angle):
    aux = np.ones((4, 1))
    aux[0] = 0.0                       # b1 = 0
    aux[1] = lon * np.cos(angle)     # b2 = l3 * np.cos(gamma)
    aux[2] = lon * np.sin(angle)     # b3 = l3 * np.sin(gamma)
    aux[3] = 1.0                       #  1
    return aux
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
class PoppySimMath (object):
    def __init__(self):
        self.coefReduction = 0.5
        # Distancias y longitudes en mm
        self.initial_l1 = 45.0
        self.initial_l2 = 107.0
        self.initial_l3 = 200.0
        self.longitud_l1 = 45.0
        self.longitud_l2 = 107.0
        self.longitud_l3 = 200.0
        self.alfa = 0.0
        self.alfa_max = np.pi/2.0
        self.alfa_min = 0.0
        self.beta = 0.0
        self.beta_max = np.pi/2.0
        self.beta_min = 0.0
        self.gamma = 0.0
        self.gamma_max = np.pi/2.0
        self.gamma_min = 0.0
        self.radio = 66.0
        self.shoulder = 210.0
        self.body = 250.0
        self.ang = [-0.7854, 0.0, 0.7854]

    # Metodo para calcular la posicion final del brazo del Poppy. Al mismo tiempo, esto nos permite poder dibujarlo.
    def moveLeftArm (self, angles):
        self.alfa = angles[0]
        self.beta = angles[1]
        self.gamma = angles[2]
        rotateMatrix = buildTransformationMatrix(self.longitud_l1, self.longitud_l2, self.alfa, self.beta)
        vector2ndSystem = point2ndSystem(self.longitud_l3, self.gamma)
        resultado = np.matmul(rotateMatrix, vector2ndSystem)

        # Posiciones en "x", "y" y "z" de los diferentes puntos que forman el diseno del Poppy,
        #         1er punto             2do punto                 3er punto           4to punto
        x_larm = [    0.0,                                    0.0, rotateMatrix[0][3], resultado[0][0]]
        y_larm = [    0.0, self.longitud_l1 * np.cos(self.alfa), rotateMatrix[1][3], resultado[1][0]]
        z_larm = [    0.0, self.longitud_l1 * np.sin(self.alfa), rotateMatrix[2][3], resultado[2][0]]

        return x_larm, y_larm, z_larm

    # Metodo para obtener los vectores que permiten dibujar la cabeza del Poppy
    def headCoordinates (self):
        u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
        x_head = (self.shoulder / 2.0) + self.radio * np.cos(u) * np.sin(v)
        y_head = self.radio * np.sin(u) * np.sin(v)
        z_head = 1.5 * self.radio + self.radio * np.cos(v)
        return x_head, y_head, z_head

    # Metodo para dibujar el hombro y el brazo derecho
    def draw_shoulder_and_rightArm(self):
        x_rarm = [0.0, self.shoulder, self.shoulder, self.shoulder, self.shoulder]
        y_rarm = [0.0, 0.0, 0.0, 0.0, self.longitud_l3]
        z_rarm = [0.0, 0.0, -self.longitud_l1, -self.longitud_l3, -self.longitud_l3]
        return x_rarm, y_rarm, z_rarm

    # Metodo para dibujar el cuerpo y la base del Poppy.
    def draw_the_body (self):
        x_body = [(self.shoulder / 2.0), (self.shoulder / 2.0)]
        y_body = [0.0, 0.0]
        z_body = [(self.radio / 2.0), -(self.longitud_l3 + self.longitud_l2 + self.longitud_l1)]

        # Distancias en mm
        x_floor = [50, 150, 150, 50, 50]
        y_floor = [-50, -50, 50, 50, -50]
        z_floor = [-(self.longitud_l3 + self.longitud_l2 + self.longitud_l1), -(self.longitud_l3 + self.longitud_l2 + self.longitud_l1), -(self.longitud_l3 + self.longitud_l2 + self.longitud_l1), -(self.longitud_l3 + self.longitud_l2 + self.longitud_l1), -(self.longitud_l3 + self.longitud_l2 + self.longitud_l1)]

        return x_body, y_body, z_body, x_floor, y_floor, z_floor
# ----------------------------------------------------------------------------------------------------------------------


# ------------------  Funcion para dibujar el Poppy  -------------------------------------------------------------------
def drawPoppyrobot(clase_robot, brazo_final, centro_imagen, titulo, ensayo, directorio):
    # Distsancias en mm
    x_axisHigh = 300
    x_axisLow = -100
    y_axisHigh = 325
    y_axisLow = -50
    z_axisHigh = 300
    z_axisLow = -100

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    fig.suptitle(titulo)

    ax.set_xlabel('X Label (mm)')
    ax.set_ylabel('Y Label (mm)')
    ax.set_zlabel('Z Label (mm)')

    ax.set_xlim3d(x_axisLow, x_axisHigh)
    ax.set_ylim3d(y_axisLow, y_axisHigh)
    ax.set_zlim3d(z_axisLow, z_axisHigh)

    ax.plot(brazo_final[0], brazo_final[1], brazo_final[2], color='b')
    ax.scatter(brazo_final[0], brazo_final[1], brazo_final[2], color='b', s=10)
    ax.scatter(centro_imagen[0], centro_imagen[1], centro_imagen[2], color='r', s=30)

    x_h, y_h, z_h = clase_robot.headCoordinates()
    x_r, y_r, z_r = clase_robot.draw_shoulder_and_rightArm()
    x_b, y_b, z_b, x_f, y_f, z_f = clase_robot.draw_the_body()
    ax.plot_wireframe(x_h, y_h, z_h, color="r")
    ax.plot(x_r, y_r, z_r, color='r')
    ax.scatter(x_r, y_r, z_r, color='r', s=5)
    ax.plot(x_b, y_b, z_b, color = 'r')
    ax.scatter (x_b, y_b, z_b, color = 'r', s = 5)
    ax.plot(x_f, y_f, z_f, color='r')
    ax.scatter(x_f, y_f, z_f, color='r', s = 5)

    plt.show()
    titulo = 'Testeo_solucion_Prueba_' + str(ensayo) + '.png'
    # plt.savefig(titulo)
    plt.close()
# ----------------------------------------------------------------------------------------------------------------------


# ------------------  Funcion para dibujar la secuencia de movimiento del brazo del Poppy  -----------------------------
def drawFullArmSequence(clase_robot, brazo, centro_imagen, titulo, ensayo, directorio):
    # Distancias en mm
    x_axisHigh = 300
    x_axisLow = -50
    y_axisHigh = 300
    y_axisLow = -50
    z_axisHigh = 300
    z_axisLow = -350

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    fig.suptitle(titulo)

    ax.set_xlabel('X Label (mm)')
    ax.set_ylabel('Y Label (mm)')
    ax.set_zlabel('Z Label (mm)')

    ax.set_xlim3d(x_axisLow, x_axisHigh)
    ax.set_ylim3d(y_axisLow, y_axisHigh)
    ax.set_zlim3d(z_axisLow, z_axisHigh)

    for n in range(0, len(brazo)):
        ax.plot(brazo[n][0], brazo[n][1], brazo[n][2], color='b')
        ax.scatter(brazo[n][0], brazo[n][1], brazo[n][2], color='b', s=10)

    x_hand_seq = [brazo[n][0][3] for n in range(0, len(brazo))]
    y_hand_seq = [brazo[n][1][3] for n in range(0, len(brazo))]
    z_hand_seq = [brazo[n][2][3] for n in range(0, len(brazo))]

    x_arrow = [0 for n in range(0, len(x_hand_seq) - 1)]
    y_arrow = [0 for n in range(0, len(y_hand_seq) - 1)]
    z_arrow = [0 for n in range(0, len(z_hand_seq) - 1)]

    for n in range(0, len(x_arrow)):
        x_arrow[n] = [x_hand_seq[n], x_hand_seq[n + 1]]
        y_arrow[n] = [y_hand_seq[n], y_hand_seq[n + 1]]
        z_arrow[n] = [z_hand_seq[n], z_hand_seq[n + 1]]

    for n in range(0, len(x_arrow)):
        aux = Arrow3D(x_arrow[n], y_arrow[n], z_arrow[n], mutation_scale=20, lw=1, arrowstyle="->", color="g")
        ax.add_artist(aux)
    ax.scatter(centro_imagen[0], centro_imagen[1], centro_imagen[2], color='r', s=30)

    x_h, y_h, z_h = clase_robot.headCoordinates()
    x_r, y_r, z_r = clase_robot.draw_shoulder_and_rightArm()
    x_b, y_b, z_b, x_f, y_f, z_f = clase_robot.draw_the_body()
    ax.plot_wireframe(x_h, y_h, z_h, color="r")
    ax.plot(x_r, y_r, z_r, color='r')
    ax.scatter(x_r, y_r, z_r, color='r', s=5)
    ax.plot(x_b, y_b, z_b, color = 'r')
    ax.scatter (x_b, y_b, z_b, color = 'r', s = 5)
    ax.plot(x_f, y_f, z_f, color='r')
    ax.scatter(x_f, y_f, z_f, color='r', s = 5)

    titulo = directorio + '/' + 'Testeo_solucion_Prueba_' + str(ensayo) + '.png'
    
    plt.savefig(titulo)
    plt.show()
    plt.close()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def drawVisualField (brazo, cent_img, experimento):
    # Distancias en mm
    x_axisHigh = 300
    x_axisLow = -100
    z_axisHigh = 300
    z_axisLow = -100

    fig, ax = plt.subplots()

    ax.set_title('Representacion campo visual')
    ax.set_ylabel('Posicion en Z (mm)')
    ax.set_xlabel('Posicion en X (mm)')

    x_rep = [0 for n in range(0, len(brazo))]
    z_rep = [0 for n in range(0, len(brazo))]

    for n in range(0, len(brazo)):
        x_rep[n] = brazo[n][0][3]
        z_rep[n] = brazo[n][2][3]

    last_dist_x = [x_rep[len(x_rep) - 1], cent_img[0]]
    last_dist_z = [z_rep[len(z_rep) - 1], cent_img[2]]

    plt.plot(x_rep, z_rep, color = 'r')
    plt.plot(last_dist_x, last_dist_z, color = 'g')
    plt.plot(cent_img[0], cent_img[2], 'bo')

    for n in range(0, len(brazo)):
        plt.plot(x_rep[n], z_rep[n], 'ro')

    plt.xlim([x_axisLow, x_axisHigh])
    plt.ylim([z_axisLow, z_axisHigh])

    a_text = 'Trayectoria_final_recorrida_prueba_0'
    aux_text = a_text + str(experimento) + '.png'
    if experimento == 'n':
        plt.show()
    else:
        plt.savefig(aux_text)
    plt.close()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def printTestSolutions3D(clase_robot, brazo_final, tamano, centro_imagen, experimento):
    # Distsancias en mm
    x_axisHigh = 300
    x_axisLow = -100
    y_axisHigh = 325
    y_axisLow = -50
    z_axisHigh = 300
    z_axisLow = -100

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    text = 'Posiciones finales en los ensayos. Numero de ensayos: ' + str(tamano)
    fig.suptitle(text)

    ax.set_xlabel('X Label (mm)')
    ax.set_ylabel('Y Label (mm)')
    ax.set_zlabel('Z Label (mm)')

    ax.set_xlim3d(x_axisLow, x_axisHigh)
    ax.set_ylim3d(y_axisLow, y_axisHigh)
    ax.set_zlim3d(z_axisLow, z_axisHigh)

    tamanoArrays = len(brazo_final[0])
    for n in range(0, len(brazo_final)):
        count00 = 0
        count01 = 0
        while count00 < tamanoArrays:
            if brazo_final[n][count00] != 0:
                count00 = count00 + 1
                count01 = count01 + 1
            else:
                count00 = tamanoArrays

        ax.plot(brazo_final[n][count01 - 1][0], brazo_final[n][count01 - 1][1], brazo_final[n][count01 - 1][2], color='b')
        ax.scatter(brazo_final[n][count01 - 1][0], brazo_final[n][count01 - 1][1], brazo_final[n][count01 - 1][2], color='b', s=10)
        ax.scatter(centro_imagen[n][0], centro_imagen[n][1], centro_imagen[n][2], color='r', s=30)

    x_h, y_h, z_h = clase_robot.headCoordinates()
    x_r, y_r, z_r = clase_robot.draw_shoulder_and_rightArm()
    x_b, y_b, z_b, x_f, y_f, z_f = clase_robot.draw_the_body()
    ax.plot_wireframe(x_h, y_h, z_h, color="r")
    ax.plot(x_r, y_r, z_r, color='r')
    ax.scatter(x_r, y_r, z_r, color='r', s=5)
    ax.plot(x_b, y_b, z_b, color='r')
    ax.scatter(x_b, y_b, z_b, color='r', s=5)
    ax.plot(x_f, y_f, z_f, color='r')
    ax.scatter(x_f, y_f, z_f, color='r', s=5)

    a_text = 'Sol_fin_en_'
    aux_text = a_text + str(tamano) + 'pruebas_y_experimento' + str(experimento) + '.png'
    plt.show()
    plt.close()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def printTestSolutions2D(brazo, proofs, cent_img, experimento):
    # Distancias en mm
    x_axisHigh = 300
    x_axisLow = -100
    z_axisHigh = 300
    z_axisLow = -100

    fig, ax = plt.subplots()

    ax.set_title('Soluciones de los testeos realizados en las pruebas')
    ax.set_ylabel('Posicion en Z (mm)')
    ax.set_xlabel('Posicion en X (mm)')

    x_rep = [1 for n in range(0, proofs)]
    z_rep = [1 for n in range(0, proofs)]

    tamanoArrays = len(brazo[0])
    for n in range(0, len(brazo)):
        count00 = 0
        count01 = 0
        while count00 < tamanoArrays:
            if brazo[n][count00] != 0:
                count00 = count00 + 1
                count01 = count01 + 1
            else:
                count00 = tamanoArrays

        x_rep[n] = brazo[n][count01 - 1][0][3]
        z_rep[n] = brazo[n][count01 - 1][2][3]

    for n in range(0, len(brazo)):
        plt.plot(x_rep[n], z_rep[n], 'ro')
        plt.plot(cent_img[n][0], cent_img[n][2], 'bo')

    plt.xlim([x_axisLow, x_axisHigh])
    plt.ylim([z_axisLow, z_axisHigh])

    a_text = 'Tray_final__'
    aux_text = a_text + str(proofs) + 'pruebas_y_experimento' + str(experimento) + '.png'
    if experimento == 'n':
        plt.show()
    else:
        plt.savefig(aux_text)
    plt.close()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def representBox (final_dist, fit, prueba, experimento):

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
    mediana_fit = np.median(fit)
    mediana_dist = np.median(final_dist)

    fit_low_lim = mediana_fit - 10.0
    fit_up_lim = mediana_fit + 10.0
    ax[0].set_xlim([fit_low_lim,  fit_up_lim])
    ax[0].boxplot(fit)
    ax[0].set_title('Distancia  final')
    ax[0].yaxis.grid(True)

    fin_low_lim = mediana_dist - 10.0
    fin_up_lim = mediana_dist + 10.0
    ax[1].set_xlim([fin_low_lim,  fin_up_lim])
    ax[1].boxplot(final_dist)
    ax[1].set_title('Distancia  final')
    ax[1].yaxis.grid(True)

    plt.show()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def createBallPosition(robot, clase):
    if clase.dev_stage == 1:
        # aux = rd.uniform(-np.pi / 2.0, np.pi / 2.0)
        aux = np.pi/3
        aux_02 = -np.pi/2
        aux03 = np.pi / 4
        ang = [aux, aux_02, aux03]
        aux_x, aux_y, aux_z = robot.moveLeftArm(ang)
        center = [aux_x[3], aux_y[3], aux_z[3]]
    elif clase.dev_stage == 2:
        # aux = rd.uniform(-np.pi / 2.0, np.pi / 2.0)
        # aux_02 = rd.uniform(-np.pi / 2.0, np.pi / 2.0)
        aux = 0.0
        aux_02 = 0.0
        aux03 = np.pi / 4
        ang = [aux, aux_02, aux03]
        aux_x, aux_y, aux_z = robot.moveLeftArm(ang)
        center = [aux_x[3], aux_y[3], aux_z[3]]
    else:
        ang = [np.pi/4.3, -np.pi/2.0, rd.uniform(-np.pi/3.0, 0.0)]
        aux_x, aux_y, aux_z = robot.moveLeftArm(ang)
        center = [aux_x[3], aux_y[3], aux_z[3]]

    return center
# ----------------------------------------------------------------------------------------------------------------------
#Modificación a la librería realizado por Steven, Ferrol 2019
#Dibuja los movimientos del plano (X,Z) correspondientes a los movimientos del brazo del robot
def draw2D(clase_robot, brazo, centro_imagen, titulo, ensayo, directorio):
    x_axisHigh = 300
    x_axisLow = -50
    z_axisHigh = 350
    z_axisLow = -350

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    fig.suptitle("2D")

    ax.set_xlabel('X Label (mm)')
    ax.set_ylabel('Z Label (mm)')

    ax.set_xlim(x_axisLow, x_axisHigh)
    ax.set_ylim(z_axisLow, z_axisHigh)

    x_arrow,z_arrow = getArrow(brazo)    
    for i in range(0,len(x_arrow)):
        x1,y1 = x_arrow[i],z_arrow[i]
        plt.plot(x1,y1, marker = '>',color='g')
        
    ax.scatter(centro_imagen[0], centro_imagen[2], color='r')

    titulo = directorio + '/' + 'Testeo_solucion_Prueba_' + str(ensayo) + '.png'
    
    #plt.savefig(titulo)
    plt.show()
    plt.close()

def getArrow(brazo):

    x_hand_seq = [brazo[n][0][3] for n in range(0, len(brazo))]
    z_hand_seq = [brazo[n][2][3] for n in range(0, len(brazo))]

    x_arrow = [0 for n in range(0, len(x_hand_seq) - 1)]
    z_arrow = [0 for n in range(0, len(z_hand_seq) - 1)]

    for n in range(0, len(x_arrow)):
        x_arrow[n] = [x_hand_seq[n], x_hand_seq[n + 1]]
        z_arrow[n] = [z_hand_seq[n], z_hand_seq[n + 1]]

    x_arrow = np.asarray(x_arrow)
    z_arrow = np.asarray(z_arrow)
    
    return x_arrow,z_arrow
#Dibuja una imagen dado una secuencia de lineas, returna una matriz de size_image X size_image 
def drawImage(size_image,x_arrow, z_arrow):

    for n in range(len(x_arrow)):
        for i in range(2):
            if(z_arrow[n][i] < 0):
                z_arrow[n][i] = z_arrow[n][i] * -1

    image = np.ones((size_image,size_image))*255
    x_arrow =  x_arrow.astype(int).flatten()
    z_arrow = (size_image-1) - z_arrow.astype(int).flatten()

    points = []
    for x in zip(x_arrow,z_arrow):
        points.append(x)

    for index, item in enumerate(points):
        if index == len(points) -1:
            break
        cv2.line(image, item, points[index + 1],[0,255,0],2) 
    return image

#Calcula el angulo correspondiente a la escala definida por los parametros de la función
def calculateAngleScale(x,x_min,x_max,y_min,y_max):
    result = []
    for i in range(len(x)):
        result.append(((x[i]-x_min)/(x_max-x_min)) * (y_max-y_min) + y_min)
    return result

#Convierte angulos en radianes
def getRadAngles(degrees):
    a = (degrees[0] * np.pi)/180.0
    b = (degrees[1] * np.pi)/180.0
    c = (degrees[2] * np.pi)/180.0

    return [a,b,c]