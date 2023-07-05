from controller import Robot
from rpyc.utils.server import ThreadedServer
from threading import Thread

from moveSearcher import MoveSearcher
from camSearcher import CamSearcher
from networkSearcher import NetworkSearcher
import utils as color

import rpyc
import keyboard
robot_instance = Robot()
TIME_STEP = int(robot_instance.getBasicTimeStep())

class Seacher(rpyc.Service):

    exposed_robot_type = "searcher"
    exposed_target_color = color.rand_color()

    def __init__(self):
        ## Robot
        self.robot = robot_instance

        ## Propiedades
        self.state = "search"
        self.box_on_top_id = -1
        self.target = None
        self.parar = False

        ## Clases auxiliares
        self.cam  = CamSearcher(self.robot, TIME_STEP)
        self.move = MoveSearcher(self.robot, TIME_STEP, self.cam)
        self.net  = NetworkSearcher(self.robot.getName())

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def swap_state(self,new_state):
        self.move.counter = 0
        self.state = new_state

    def exposed_get_net(self):
        return self.net

    def exposed_get_color(self):
        if(Seacher.exposed_target_color == color.color_red):
            return "red"
        else:
            return "blue"

    def center_robot(self):
        self.target = self.cam.get_camera_target(color.color_green)
        if(self.target == None):
            self.move.turn_left()
        else:
            self.cam.update_target(self.target)
            if(self.target.pos_x < self.move.left_margin):
                self.move.turn_left()
            elif(self.target.pos_x > self.move.right_margin):
                self.move.turn_right()
            else:
                return True
        return False
    
    def change_color(self):
        next_color = self.net.get_target_color()
        if(next_color== "red"):
            Seacher.exposed_target_color = color.color_red
        elif(next_color== "blue"):
            Seacher.exposed_target_color = color.color_blue
        else:
            Seacher.exposed_target_color = color.rand_color()

    def stop_by_key(self):
        name = self.robot.getName()

        if (keyboard.is_pressed('g') and name == "robot_1"):
            print("paramos 1")
            self.parar = True
        if(keyboard.is_pressed('b') and name == "robot_1"):
            print("continuamos 1")
            self.parar = False
        
        if (keyboard.is_pressed('h') and name == "robot_2"):
            self.parar = True
        if(keyboard.is_pressed('n') and name == "robot_2"):
            self.parar = False
        
        if (keyboard.is_pressed('j') and name == "robot_3"):
            self.parar = True
        if(keyboard.is_pressed('m') and name == "robot_3"):
            self.parar = False
        
        

    def main_loop(self):
        reposition_before_searching = False

        while self.robot.step(TIME_STEP) != -1:
            self.stop_by_key()

            if(self.parar == True):
                self.move.stop()
                continue

            if(self.state == "search"): ## ESTADO BÚSQUEDA
                if(self.move.move_to_search()):
                    self.change_color()

                if(self.box_on_top_id == -1):
                    color_to_search = Seacher.exposed_target_color
                    next_state = "located"
                else:
                    color_to_search = color.zone_colors(Seacher.exposed_target_color)
                    next_state = "store"

                self.target = self.cam.get_camera_target(color_to_search)

                if(self.target != None):
                    self.swap_state(next_state)

            elif(self.state == "located"): ## ESTADO LOCALIZADO
                
                if(self.cam.update_target(self.target) == False):
                    self.swap_state("search")
                else:
                    if(self.cam.target_reached(self.target, 0.3)):
                        self.net.load_box_on_robot(self.target.id)
                        self.box_on_top_id = self.target.id

                        self.swap_state("search")
                    else:
                        self.move.move_to_target(self.target)

            elif(self.state == "store"): ## ESTADO ALMACENAR
                if(reposition_before_searching):
                    if(self.center_robot()):
                        self.swap_state("search")
                        reposition_before_searching = False
                    continue

                if(self.cam.update_target(self.target) == False):
                    self.swap_state("search")
                else:
                    if(self.cam.target_reached(self.target, 0.09)):
                        if(Seacher.exposed_target_color == color.color_red):
                            self.net.store_box_on_zone(self.target.id, self.box_on_top_id, "red")
                            self.net.add_box_ammount("red")
                        else:
                            self.net.store_box_on_zone(self.target.id, self.box_on_top_id, "blue")
                            self.net.add_box_ammount("blue")
                        
                        self.box_on_top_id = -1
                        reposition_before_searching = True
                        self.change_color()
                    else:
                        self.move.move_to_target(self.target)

seacher = Seacher()
ThreadedServer(seacher, hostname="127.0.0.1", port=seacher.net.port).start()