from math import atan2, pi, sqrt

## --- GPS ---
def get_robot_pos(gps):
    abs_pos = gps.getValues()
    x = round(abs_pos[0],3)
    y = round(abs_pos[1],3)
    return [x,y]

## --- Brujula ---
def orientacion_en_grados(compass):
    values = compass.getValues()
    y, x, z = values
    rad = atan2(y, x)
    bearing = rad * 180 / pi
    if (bearing < 0.0): bearing += 360.0
    return bearing

## --- Ruedas ---

def rotar_derecha(lwheels, rwheels, vel_rotacion):
    [w.setVelocity(vel_rotacion) for w in lwheels]
    [w.setVelocity(-vel_rotacion) for w in rwheels]

def rotar_izquierda(lwheels, rwheels, vel_rotacion):
    [w.setVelocity(vel_rotacion) for w in rwheels]
    [w.setVelocity(-vel_rotacion) for w in lwheels]

def avanzar(wheels, vel_avanzar):
    [w.setVelocity(vel_avanzar) for w in wheels]

def parar(wheels):
    [w.setVelocity(0) for w in wheels]

## --- Sensores ---

def detectar_obstaculo(sensores):
    min_val = 30.0

    ds_l = sensores[0].value
    ds_c = sensores[1].value
    ds_r = sensores[2].value

    if(ds_l < min_val):
        return "left"
    elif(ds_r < min_val):
        return "right"
    elif(ds_c < min_val):
        return "center"
    
    return "nada"

## --- Calculos ---
 
def calc_grados_destino(pos_actual,destino):
    pos_actual_x, pos_actual_y = pos_actual
    destino_x, destino_y = destino

    angulo = atan2(destino_y-pos_actual_y, destino_x-pos_actual_x) * (180/pi)
    if (angulo < 0): angulo += 360
    return angulo

def calc_distancia_destino(pos_actual, destino):
    pos_actual_x, pos_actual_y = pos_actual
    destino_x, destino_y = destino
    
    a = (destino_x - pos_actual_x)**2
    b = (destino_y - pos_actual_y)**2

    distancia = sqrt(a+b)
    return distancia

def calc_sentido_giro(grados_destino, orientacion_actual):
    if(abs(grados_destino - orientacion_actual) <= 2):
        giro = 0
    else:
        alterno = orientacion_actual + 180
        if(alterno > 360): alterno -= 360

        if(orientacion_actual < 180):
            if(grados_destino > orientacion_actual and grados_destino < alterno):
                giro = -1
            else:
                giro = 1
        else:
            if(grados_destino > orientacion_actual or grados_destino < alterno):
                giro = -1
            else:
                giro = 1
    return giro