import poppySimRobot as psr
import numpy as np
def main():
    poppy = psr.PoppySimMath()
    arm_pos = poppy.moveLeftArm(psr.getRadAngles([5,10,5]))
    arm_pos2 = poppy.moveLeftArm(psr.getRadAngles([-15,25,25]))
    arm_pos3 = poppy.moveLeftArm(psr.getRadAngles([10,10,5]))
    arm_pos4 = poppy.moveLeftArm(psr.getRadAngles([5,8,5]))   
    vec = [arm_pos,arm_pos2,arm_pos3,arm_pos4]
    print(arm_pos)#X,Y,Z y el -1 es el resultado en ese eje
    #def drawPoppyrobot(clase_robot, brazo_final, centro_imagen, titulo, ensayo, directorio):
    #psr.drawPoppyrobot(poppy, arm_pos, [0.0, 100.0, 100.0], 'Prueba', 2, 'casa')
    #psr.drawFullArmSequence(poppy,vec,[0.0, 100.0, 100.0],'Prueba',2,'./')
    #psr.draw2D(poppy,vec,[0.0, 100.0, 100.0],'Prueba',2,'./')
    print(psr.calculateAngleScale([0.5,1],0.0,1.0,30.0,90.0))
    #psr.drawImage()
    
if __name__ == '__main__':
    main()