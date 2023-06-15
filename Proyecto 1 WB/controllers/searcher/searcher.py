from controller import Robot
from rpyc.utils.server import ThreadedServer
from threading import Thread

from moveSearcher import MoveSearcher
from camSearcher import CamSearcher
import utils as color

import rpyc



robot_instance = Robot()
TIME_STEP = int(robot_instance.getBasicTimeStep())

class Seacher(rpyc.Service):

    def __init__(self):
        ## Robot
        self.robot = robot_instance
        self.robot_number = int(self.robot.getName().split("_")[1])
        self.port = 3000 + self.robot_number

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

        ## Propiedades
        self.state = "search"
        self.box_on_top_id = -1
        self.target_color = color.color_red
        self.target = None

        ## Clases auxiliares
        self.move = MoveSearcher(self.robot, TIME_STEP)
        self.cam  = CamSearcher(self.robot, TIME_STEP)

         
    def main_loop(self):
        supervisor = rpyc.connect("127.0.0.1", 3000)

        while self.robot.step(TIME_STEP) != -1:
            
            if(self.state == "search"): ## ESTADO BÚSQUEDA
                self.move.move_to_search()

                if(self.box_on_top_id == -1):
                    color_to_search = self.target_color
                else:
                    color_to_search = color.zone_colors(self.target_color)

                self.target = self.cam.get_camera_target(color_to_search)

                if(self.target != None):
                    self.state = "located"

            elif(self.state == "located"): ## ESTADO LOCALIZADO
                
                if(self.cam.update_target(self.target) == False):
                    self.state = "search"
                else:
                    print(self.target.size)
                    if(self.cam.target_reached(self.target, 0.3)):
                        supervisor.root.load_box(self.robot.getName(), self.target.id)
                        self.state = "store"
                        self.carrying_box_id = self.target.id
                    else:
                        self.move.move_to_target(self.target, self.cam.cam_left_margin, self.cam.cam_right_margin)

            elif(self.state == "store"): ## ESTADO ALMACENAR
                pass

seacher = Seacher()
ThreadedServer(seacher, hostname="127.0.0.1", port=seacher.port).start()