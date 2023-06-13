from controller import Robot
from rpyc.utils.server import ThreadedServer
from threading import Thread
import keyboard
import sys
import rpyc
import time
sys.path.insert(1, 'C:\\Users\\Lucas\\Desktop\\TFG\\Proyecto 1 WB\\controllers\\utils')

import utils as ut
import ports as port


robot_instance = Robot()
TIME_STEP = int(robot_instance.getBasicTimeStep())
rotar = 0
velocidad = 0

cam_margin = 20
goal_margin = 26
ds_umbral = 25

class Robot_RPYC(rpyc.Service):

    def __init__(self):

        ## Robot
        self.robot = robot_instance
        self.robot_number = int(self.robot.getName().split("_")[1])
        self.port = 3000 + self.robot_number

        ## SENSORES
        self.ds_l = self.robot.getDevice('ds_left')
        self.ds_r = self.robot.getDevice('ds_right')
        self.ds_c = self.robot.getDevice('ds_center')
        self.ir_l = self.robot.getDevice('ir_left')
        self.ir_r = self.robot.getDevice('ir_right')

        sensors = [self.ds_l, self.ds_r, self.ds_c, self.ir_l, self.ir_r]
        [s.enable(TIME_STEP) for s in sensors]

        ## RUEDAS
        w1 = self.robot.getDevice('wheel1')
        w2 = self.robot.getDevice('wheel2')
        w3 = self.robot.getDevice('wheel3')
        w4 = self.robot.getDevice('wheel4')
        self.wheels = [w1,w2,w3,w4]
        self.lwheels = [w1,w3]
        self.rwheels = [w2,w4]

        for w in self.wheels:
            w.setPosition(float('inf'))
            w.setVelocity(0.0)

        ## CÁMARA
        self.camera = self.robot.getDevice('camera')
        self.camera.enable(TIME_STEP)
        self.camera.recognitionEnable(TIME_STEP)

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

        ## Propiedades
        self.state = ""
        self.color_target = "red"
        self.cam_left_margin = self.camera.getHeight()/2 - cam_margin
        self.cam_right_margin = self.camera.getHeight()/2 + cam_margin

        self.last_obstacle = ""
        self.reposition_obtacle = False
        self.counter = 0

        ## cambiar mas tarde
        self.target_id = -1
    
    def get_camera_target(self,list_objects):
        closest_id = 0
        tam_max = 0

        for object in list_objects:
            if(True): #añadir reglas colores

                tam2D = object.getSizeOnImage()
                tam = tam2D[0] + tam2D[1]

                if(tam > tam_max):
                    closest_id = object.getId()
                    tam_max = tam

        self.target_id = closest_id

    def avoid_obstacles(self):
        left  = int(self.ds_l.getValue())
        center = int(self.ds_c.getValue())
        right = int(self.ds_r.getValue())

        if(left < ds_umbral):
            self.last_obstacle = "left"
            self.reposition_obtacle = True
            ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
            return True
        
        if(right < ds_umbral):
            self.last_obstacle = "right"
            self.reposition_obtacle = True
            ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
            return True
        
        if(center < ds_umbral):
            if(self.last_obstacle == "left"):
                ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
            else:
                ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
            self.reposition_obtacle = True
            return True
        
        if(self.reposition_obtacle):
            if(self.counter == 200):
                self.reposition_obtacle = False
                self.counter = 0
                return False
            else:
                ut.avanzar(self.wheels,velocidad)
                self.counter += 1
                return True
        
        return False

    def move_to_target(self, target):
        target_position = target.getPositionOnImage()[0]

        avoid = self.avoid_obstacles()
        if(avoid): return

        if(target_position < self.cam_left_margin):
            ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
        elif(target_position > self.cam_right_margin):
            ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
        else:
            ut.avanzar(self.wheels,velocidad)
    
    def target_reached(self, target):
        left   = int(self.ds_l.getValue())
        center = int(self.ds_c.getValue())
        right  = int(self.ds_r.getValue())
        target_size = target.getSizeOnImage()
        goal_size = self.camera.getWidth()*0.4

        condition1 = left <= goal_margin or center <= goal_margin or right <= goal_margin
        condition2 = (target_size[0] >= goal_size or target_size[1] >= goal_size)

        return (condition1 and condition2)
    
    def get_target_from_list(self,list_ro):
        for ro in list_ro:
            if(ro.getId() == self.target_id):
                return ro
        return None
    
    def locate_store(self, color, ):
        pass


    def main_loop(self):
        supervisor = rpyc.connect("127.0.0.1", port.SUPERVISOR_PORT)
        self.state = "search"
        while self.robot.step(TIME_STEP) != -1:

            if(self.state == "search"):
                list_ro = self.camera.getRecognitionObjects()

                if(len(list_ro) != 0):
                    self.get_camera_target(list_ro)
                    self.state = "located"
                else:
                    ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)

            elif(self.state == "located"):
                list_ro = self.camera.getRecognitionObjects()
                target = self.get_target_from_list(list_ro)

                if(target != None):
                    if(self.target_reached(target)):
                        supervisor.root.load_box(self.robot.getName(), target.getId())
                        self.state = "store"
                    else:
                        self.move_to_target(target)
                else:
                    if(self.last_obstacle == "right"):
                        ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
                    else:
                        ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)

            elif(self.state == "store"):
                list_ro = self.camera.getRecognitionObjects()
                target = self.get_target_from_list(list_ro)







robot_rpyc = Robot_RPYC()
ThreadedServer(robot_rpyc, hostname="127.0.0.1", port=robot_rpyc.port).start()






    


