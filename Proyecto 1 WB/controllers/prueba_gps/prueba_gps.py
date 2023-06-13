from controller import Robot
from math import atan2, pi, sqrt

TIME_STEP = 16
robot = Robot()

## GPS
gps = robot.getDevice('gps')
gps.enable(TIME_STEP)

def get_robot_pos():
    abs_pos = gps.getValues()
    x = round(abs_pos[0],3)
    y = round(abs_pos[1],3)
    return [x,y]

## BRUJULA
compass = robot.getDevice('compass')
compass.enable(TIME_STEP)

def orientacion_en_grados():
    values = compass.getValues()
    y, x, z = values
    rad = atan2(y, x)
    bearing = rad * 180 / pi
    if (bearing < 0.0): bearing += 360.0
    return bearing

def calc_distancia_destino(pos_actual, destino):
    pos_actual_x, pos_actual_y = pos_actual
    destino_x, destino_y = destino
    
    a = (destino_x - pos_actual_x)**2
    b = (destino_y - pos_actual_y)**2

    distancia = sqrt(a+b)

    return distancia

def print_compass():
    values = compass.getValues()
    values_format = [round(x,3) for x in values]
    x,y = values_format
    print(f"[{x},{y}]")

## RUEDAS
w1 = robot.getDevice('wheel1')
w2 = robot.getDevice('wheel2')
w3 = robot.getDevice('wheel3')
w4 = robot.getDevice('wheel4')
wheels = [w1,w2,w3,w4]
lwheels = [w1,w3]
rwheels = [w2,w4]

for w in wheels:
    w.setPosition(float('inf'))
    w.setVelocity(0.0)


vel_rotacion = 1
vel_avanzar = 2
def rotar_derecha():
    [w.setVelocity(vel_rotacion) for w in lwheels]
    [w.setVelocity(0) for w in rwheels]

def rotar_izquierda():
    [w.setVelocity(vel_rotacion) for w in rwheels]
    [w.setVelocity(0) for w in lwheels]

def avanzar():
    [w.setVelocity(vel_avanzar) for w in lwheels]
    [w.setVelocity(vel_avanzar) for w in rwheels]

def parar():
    [w.setVelocity(0) for w in lwheels]
    [w.setVelocity(0) for w in rwheels]


def calc_grados_origen_destino(origen,destino):
    origen_x, origen_y = origen

    destino_x, destino_y = destino

    angulo = atan2(destino_y-origen_y, destino_x-origen_x) * (180/pi)
    if (angulo < 0): angulo += 360
    return angulo

def calc_giro(destino, orientacion):
    if(abs(destino - orientacion) <= 2):
        giro = 0
    else:
        alterno = orientacion + 180
        if(alterno > 360): alterno -= 360

        if(orientacion < 180):
            if(destino > orientacion and destino < alterno):
                giro = -1
            else:
                giro = 1
        else:
            if(destino > orientacion or destino < alterno):
                giro = -1
            else:
                giro = 1
    return giro


def main():
    while robot.step(TIME_STEP) != -1:
        pos = get_robot_pos()
        destino = [0,0]

        grados_destino = calc_grados_origen_destino(pos,destino)
        grados_orientacion = orientacion_en_grados()
        giro = calc_giro(grados_destino,grados_orientacion)

        distancia = calc_distancia_destino(pos,destino)
        if(distancia <= 0.2):
            print("He llegado!")
            parar()
            break

        if(giro == 0):
            avanzar()

        elif(giro == -1):
            rotar_izquierda()
        elif(giro == 1):
            rotar_derecha()

main()
    