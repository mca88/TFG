from controller import Robot, Camera

TIME_STEP = 128
robot = Robot()

##RUEDAS
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

##CÁMARA
cam = robot.getDevice('CAM')
motor_camara = robot.getDevice('motor_camara')
cam.enable(TIME_STEP)
cam.recognitionEnable(TIME_STEP)

motor_camara.setPosition(float('inf'))
motor_camara.setVelocity(0.0)


#SENSORES
ds_l = robot.getDevice('ds_left')
ds_r = robot.getDevice('ds_right')
ds_c = robot.getDevice('ds_center')

sensors = [ds_l, ds_r, ds_c]
[s.enable(TIME_STEP) for s in sensors]

def detectar_amarillo(colores):
    rojo = colores[0]
    verde = colores[1]
    azul = colores[2]
    
    return True if rojo == 1 and verde == 1 and azul == 0 else False
    
def ajustar_camara_eje_y(y):
    if(y < 300):
        motor_camara.setVelocity(-0.05)
    elif(y > 350):
        motor_camara.setVelocity(0.05)
    else:
        motor_camara.setVelocity(0)

def buscar_objeto(objetos):
    for o in objetos:
        o_colors = o.getColors()
        if(detectar_amarillo(o_colors)):
            o_position = o.getPositionOnImage()
            eje_x = o_position[0]
            eje_y = o_position[1]

            return (eje_x, eje_y)
    
    return (-1,-1)

vel_rotacion = 0.3
vel_avanzar = 2
def rotar_derecha():
    [w.setVelocity(vel_rotacion) for w in lwheels]
    [w.setVelocity(0) for w in rwheels]

def rotar_izquierda():
    [w.setVelocity(vel_rotacion) for w in rwheels]
    [w.setVelocity(0) for w in lwheels]

def avanzar_si_centrado(eje_x):
    if(eje_x < 330 and eje_x > 310):
        [w.setVelocity(vel_avanzar) for w in lwheels]
        [w.setVelocity(vel_avanzar) for w in rwheels]

def avanzar():
    [w.setVelocity(vel_avanzar) for w in lwheels]
    [w.setVelocity(vel_avanzar) for w in rwheels]

def centrar_robot_objeto(pos_x):
    if(pos_x > 325):
        rotar_derecha()
    elif(pos_x < 315):
        rotar_izquierda()

min_val = 20.0
max_val = 30.0

def valores_sensores():
    return (ds_l.value, ds_c.value, ds_r.value)

def detectar_obstaculo():
    l,c,r = valores_sensores()

    if(l < min_val):
        return "left"
    elif(r < min_val):
        return "right"
    elif(c < min_val):
        return "center"
    
    return "nada"

def eviar_obstaculo(obstaculo):
    if obstaculo == "left":
        rotar_derecha()
    
    elif obstaculo == "right":
        rotar_izquierda()

    else: 
        rotar_izquierda()

i = 30
obstaculo = "nada"
ultimo_obstaculo = "nada"
while robot.step(TIME_STEP) != -1:
    i+=1
    if i > 30:
        i = 30
    
    ro = cam.getRecognitionObjects()

    obstaculo = detectar_obstaculo()

    if obstaculo != "nada":
        i = 0
        ultimo_obstaculo = obstaculo
        print(obstaculo)
        eviar_obstaculo(obstaculo)

    if(i == 30):
        pos_x, pos_y = buscar_objeto(ro) 

        if pos_y != -1:
            ajustar_camara_eje_y(pos_y)
            centrar_robot_objeto(pos_x)
            avanzar_si_centrado(pos_x)
        else:
            print(f"AQUI: {obstaculo}")
            motor_camara.setVelocity(0)
            if(ultimo_obstaculo == "left"):
                rotar_izquierda()
            elif(ultimo_obstaculo == "right"):
                rotar_derecha()
            else:
                rotar_izquierda()
    elif i != 30 and obstaculo == "nada":
        print(i)
        avanzar()
