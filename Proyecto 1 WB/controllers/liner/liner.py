from controller import Robot
from rpyc.utils.server import ThreadedServer
from threading import Thread

from moveLiner import MoveLiner
from networkLiner import NetworkLiner
from utils import States as st

import rpyc


robot_instance = Robot()
TIME_STEP = int(robot_instance.getBasicTimeStep())

class Liner(rpyc.Service):

    exposed_robot_type = "liner"
    exposed_store_status = False
    exposed_target_color = None

    def __init__(self):

        ## Robot
        self.robot = robot_instance
        
        ## Propiedades
        self.state = st.yellow_line
        self.box_on_top_id = None
        self.change_box_id = False
        self.wait_status = False

        ## Clases auxiliares
        self.move = MoveLiner(self.robot, TIME_STEP)
        self.net  = NetworkLiner(self.robot.getName())

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def exposed_set_box_id(self, new_id):
        self.box_on_top_id = new_id

    def exposed_get_net(self):
        return self.net

    def wait(self, segs):
        if(self.wait_status):
            if(self.move.sleep_robot(segs)): 
                self.wait_status = False

    def state_changer(self):
        line_color = self.move.get_line_color()

        if(self.state == st.yellow_line):
            if(line_color == "green"):
                self.state = st.choose_target
        
        if(self.state == st.choose_target):
            if(line_color == "black"):
                self.state = st.move_zone
                self.move.turn = None

        if(self.state == st.move_zone):
            if(line_color == "red" or line_color == "blue"):
                self.state = st.pick_up_box
                self.wait_status = False

        if(self.state == st.pick_up_box):
            if(self.box_on_top_id != None):
                self.state = st.turn_store
                self.net.substract_box_ammount(Liner.exposed_target_color)

        if(self.state == st.turn_store):
            if(line_color == "black"):
                self.state = st.move_store
                self.wait_status = False

        if(self.state == st.move_store):
            if(line_color == "yellow"):
                self.state = st.store_box

        if(self.state == st.store_box):
            if(self.box_on_top_id == None):
                self.state = st.yellow_line

    def main_loop(self):

        # if(self.robot.getName() == "robot_4"):
        #     self.net.start_coordinator_election()
        
        while self.robot.step(TIME_STEP) != -1:
            self.state_changer()
            if(self.state == st.yellow_line):
                self.move.follow_line("yellow")

            if(self.state == st.choose_target):

                if(Liner.exposed_target_color == None):
                    Liner.exposed_target_color = self.net.choose_target_color()

                if(Liner.exposed_target_color == "red"):
                    self.move.turn_right()
                elif(Liner.exposed_target_color == "blue"):
                    self.move.turn_left()

            if(self.state == st.move_zone):
                self.move.follow_line("black")

            if(self.state == st.pick_up_box):
                if(self.wait_status == False):
                    self.wait_status = self.net.load_box_on_robot(Liner.exposed_target_color)

                self.wait(3)

            if(self.state == st.turn_store):
                if(Liner.exposed_target_color == "red"):
                        self.move.turn_right()
                else:
                    self.move.turn_left()
            
            if(self.state == st.move_store):

                if(self.move.get_line_color() == "gray" and Liner.exposed_store_status == False):
                    if(self.wait_status == True):
                        self.wait(1)
                        continue
                    if(self.net.check_store_status()):
                        Liner.exposed_store_status = True
                        self.wait_status = False
                    else:
                        self.wait_status = True
                else:
                    self.move.follow_line("black")
                
            if(self.state == st.store_box):
                if(self.move.get_line_color() != "yellow"):
                    self.change_box_id = True
                    if(Liner.exposed_target_color == "red"):
                        self.move.turn_right()
                    else:
                        self.move.turn_left()
                if(self.move.get_line_color() == "yellow" and self.change_box_id):
                    self.net.store_box_on_zone(self.box_on_top_id)
                    self.box_on_top_id = None
                    self.change_box_id = False
                    self.wait_status = False
                    Liner.exposed_store_status = False
                    Liner.exposed_target_color = None
                    
liner = Liner()
ThreadedServer(liner, hostname="127.0.0.1", port=liner.net.port).start()