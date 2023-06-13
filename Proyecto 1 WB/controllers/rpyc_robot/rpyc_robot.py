import rpyc
import sys
from threading import Thread
from rpyc.utils.server import ThreadedServer
from controller import Robot

sys.path.insert(1, 'C:\\Users\\Lucas\\Desktop\\TFG\\Proyecto 1 WB\\controllers\\utils')
import utils as ut
import ports as pt

TIME_STEP = 16
robot = Robot()

name = robot.getName()
number = int(name.split("_")[1])

max_robots = 8

port = 3000 + number
follow_port = port + 1

print(f"Soy el robot {number} y voy a seguir a {follow_port - 3000}")

if(follow_port > 3000 + max_robots):
    follow_port = 3001

vel_avanzar = 4
vel_rotar = 4


class RPYC_Robot(rpyc.Service):
    exposed_pos = [0,0]

    def __init__(self):

        ## Robot
        self.robot = robot
        self.name = self.robot.getName()

        ## Sensores
        self.ds_l = self.robot.getDevice('ds_left')
        self.ds_c = self.robot.getDevice('ds_center')
        self.ds_r = self.robot.getDevice('ds_right')

        self.sensors = [self.ds_l, self.ds_c, self.ds_r]
        [s.enable(TIME_STEP) for s in self.sensors]

        ## GPS
        self.gps = self.robot.getDevice('gps')
        self.gps.enable(TIME_STEP)

        ## BRUJULA
        self.compass = self.robot.getDevice('compass')
        self.compass.enable(TIME_STEP)

        ## RUEDAS
        w1 = self.robot.getDevice('wheel1')
        w2 = self.robot.getDevice('wheel2')
        w3 = self.robot.getDevice('wheel3')
        w4 = self.robot.getDevice('wheel4')
        self.wheels = [w1,w2,w3,w4]
        for w in self.wheels:
            w.setPosition(float('inf'))
            w.setVelocity(0.0)

        self.lwheels = [w1,w3]
        self.rwheels = [w2,w4]

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def follow_robot(self, pos, destino):
        pos = ut.get_robot_pos(self.gps)

        grados_destino = ut.calc_grados_destino(pos,destino)
        grados_orientacion = ut.orientacion_en_grados(self.compass)
        giro = ut.calc_sentido_giro(grados_destino,grados_orientacion)
 
        if(giro == 0):
            ut.avanzar(self.wheels, vel_avanzar)
        elif(giro == -1):
            ut.rotar_izquierda(self.lwheels, self.rwheels, vel_rotar)
        elif(giro == 1):
            ut.rotar_derecha(self.lwheels, self.rwheels, vel_rotar)

    def destino_cumplido(self, pos, destino):
        distancia = ut.calc_distancia_destino(pos,destino)
        if(distancia <= 0.3):
            return True
        else:
            return False


    def main_loop(self):
        i_timer = 50
        i = i_timer
        obstaculo = "nada"

        conn = rpyc.connect("127.0.0.1", follow_port)

        while self.robot.step(TIME_STEP) != -1:
            ## Modificamos la posición para que el resto de robots la conozcan
            RPYC_Robot.exposed_pos = ut.get_robot_pos(self.gps)
            pos_actual = ut.get_robot_pos(self.gps)

            ## Obtenemos la posicion destino
            destino = conn.root.pos

            i += 1
            if i > i_timer:
                i = i_timer
            
            if(number == 8):
                obstaculo = ut.detectar_obstaculo(self.sensors)
            else:
                obstaculo =  "nada"

            if(obstaculo == "left"):
                i = 0
                ut.rotar_derecha(self.lwheels, self.rwheels, vel_rotar)
            elif(obstaculo == "right"):
                i = 0
                ut.rotar_izquierda(self.lwheels, self.rwheels, vel_rotar)
            elif(obstaculo == "center"):
                i = 0
                ut.rotar_izquierda(self.lwheels, self.rwheels, vel_rotar)
            elif(obstaculo == "nada"):
                
                if(i == i_timer):
                    if(follow_port == 3001):
                        ut.avanzar(self.wheels, vel_avanzar)
                    else:
                        self.follow_robot(pos_actual, destino)
                else:
                    ut.avanzar(self.wheels, vel_avanzar)

            if(self.destino_cumplido(pos_actual, destino)):
                ut.parar(self.wheels)
     

r = RPYC_Robot()
ThreadedServer(r, hostname="127.0.0.1", port=port).start()
