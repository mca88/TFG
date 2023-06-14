from controller import Robot
from rpyc.utils.server import ThreadedServer
from threading import Thread
import keyboard
import sys
import rpyc
import random
sys.path.insert(1, 'C:\\Users\\Lucas\\Desktop\\TFG\\Proyecto 1 WB\\controllers\\utils')

import utils as ut
import ports as port


robot_instance = Robot()
TIME_STEP = int(robot_instance.getBasicTimeStep())

rotar = 3
velocidad = 5

cam_margin = 20
ds_umbral = 15
color_red    = [1,0,0]
color_blue   = [0,0,1]
color_yellow = [1,1,0]

class Seacher(rpyc.Service):

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
        self.state = "search"
        self.color_target = color_red
        self.cam_left_margin = self.camera.getHeight()/2 - cam_margin
        self.cam_right_margin = self.camera.getHeight()/2 + cam_margin

        self.reposition_obtacle = False
        self.reposition_after_pick = False
        self.reposition_after_store = False
        self.full_turning = False
        self.counter = 0

        ## cambiar mas tarde
        self.target_id = -1
        self.carrying_box_id = -1
        self.search_state = 1
        self.rand_turn = 1

    def rotate_full_right(self):
        if(self.counter == 150):
            self.counter = 0
            self.full_turning = False
        else:
            self.counter += 1
            ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
            
    def move_forward_a_bit(self):
        if(self.counter == 200):
            self.counter = 0
            self.reposition_after_pick = False
        else:
            self.counter += 1
            ut.avanzar(self.wheels,velocidad)

    def turn(self):
        if(self.counter == 300):
            self.counter = 0
            self.reposition_after_store = False
        else:
            self.counter += 1
            ut.rotar_derecha(self.lwheels, self.rwheels, rotar)


    def extract_list_colors(self,color_object):
        red = int(color_object[0])
        green = int(color_object[1])
        blue = int(color_object[2])
        return [red,green,blue]
    
    def get_target_from_list(self, target_id, list_ro):
        for ro in list_ro:
            if(ro.getId() == target_id):
                return ro
        return None
    
    def get_camera_target(self,ro_objects):
        closest_id = -1
        tam_max = 0

        for ro_object in ro_objects:
            ro_color = self.extract_list_colors(ro_object.getColors())
            if(ro_color == self.color_target): 
                tam2D = ro_object.getSizeOnImage()
                tam = tam2D[0] + tam2D[1]

                if(tam > tam_max):
                    closest_id = ro_object.getId()
                    tam_max = tam

        self.target_id = closest_id

    def avoid_obstacles(self):
        left  = int(self.ds_l.getValue())
        center = int(self.ds_c.getValue())
        right = int(self.ds_r.getValue())

        obstacle_left = (left <= ds_umbral)
        obstacle_center = (center <= ds_umbral)
        obstacle_right = (right <= ds_umbral)
        
        if(obstacle_left and obstacle_right):
            self.full_turning = True
            return True
        
        elif(obstacle_left):
            self.reposition_obtacle = True
            ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
            return True
        
        elif(obstacle_right):
            self.reposition_obtacle = True
            ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
            return True
        
        elif(obstacle_center):
            self.reposition_obtacle = True
            ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
            return True

        elif(self.reposition_obtacle):
            if(self.counter == 150):
                self.reposition_obtacle = False
                self.counter = 0
                return False
            else:
                ut.avanzar(self.wheels,velocidad)
                self.counter += 1
                return True
        
        return False

    def move_to_target(self, target):
        if(self.full_turning):
            self.rotate_full_right()
            return
        if(target == None):
            self.state = "search"
            self.target_id = -1
            return
        
        target_position = target.getPositionOnImage()[0]
        avoid = self.avoid_obstacles()
        if(avoid): return

        if(target_position < self.cam_left_margin):
            ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
        elif(target_position > self.cam_right_margin):
            ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
        else:
            ut.avanzar(self.wheels,velocidad)

    def search_target(self):
        if(self.avoid_obstacles()):
            self.search_state = 1
            return

        if(self.search_state == 1):
            if(self.counter == 150):
                self.counter = 0
                self.search_state = 2
                self.rand_turn = random.randint(0, 1)
            else:
                ut.avanzar(self.wheels,velocidad)
                self.counter += 1

        elif(self.search_state == 2):
            if(self.counter == 150):
                self.counter = 0
                self.search_state = 1
            else:  
                if(self.rand_turn == 0):
                    ut.rotar_izquierda(self.lwheels, self.rwheels, rotar)
                else:
                    ut.rotar_derecha(self.lwheels, self.rwheels, rotar)
                self.counter += 1
    
    def target_reached(self, target, percentage):
        if(target == None): return False
        size2D = target.getSizeOnImage()
        target_size = size2D[0] * size2D[1]
        cam_size = self.camera.getWidth() * self.camera.getHeight()
        condition = (target_size >= cam_size*percentage)

        return (condition)
    
    def locate_store(self, list_ro, color):
        for ro in list_ro:
            color_ro = self.extract_list_colors(ro.getColors())
            if(color == color_ro):
                return ro.getId()
        return None


    def main_loop(self):
        supervisor = rpyc.connect("127.0.0.1", port.SUPERVISOR_PORT)

        while self.robot.step(TIME_STEP) != -1:
            if(self.state == "search"):
                if(self.reposition_after_store):
                    self.turn()
                    continue

                self.search_target()
                list_ro = self.camera.getRecognitionObjects()
                if(len(list_ro) != 0):
                    self.get_camera_target(list_ro)
                    
                if(self.target_id != -1):
                    self.state = "located"
                    self.search_state = 1
                    self.counter = 0

            elif(self.state == "located"):
                list_ro = self.camera.getRecognitionObjects()
                target = self.get_target_from_list(self.target_id, list_ro)

                if(self.target_reached(target, 0.3)):
                    supervisor.root.load_box(self.robot.getName(), target.getId())
                    self.state = "store"
                    self.carrying_box_id = target.getId()
                    self.reposition_after_pick = True
                else:
                    self.move_to_target(target)

            elif(self.state == "store"):
                if(self.reposition_after_pick):
                    self.move_forward_a_bit()
                    continue
                
                list_ro = self.camera.getRecognitionObjects()
                store_id = self.locate_store(list_ro, color_yellow)
                target = self.get_target_from_list(store_id, list_ro)

                if(target != None):
                    if(self.target_reached(target, 0.10)):
                        supervisor.root.store_box(target.getId(), self.carrying_box_id)
                        self.state = "search"
                        self.reposition_after_store = True
                    else:
                        self.move_to_target(target)
                else:
                    if(self.avoid_obstacles() == False):
                        ut.rotar_derecha(self.lwheels, self.rwheels, rotar)

seacher = Seacher()
ThreadedServer(seacher, hostname="127.0.0.1", port=seacher.port).start()






    


