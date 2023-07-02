from controller import Robot
from rpyc.utils.server import ThreadedServer
from threading import Thread
from moveLiner import MoveLiner
from utils import States as st

import rpyc


robot_instance = Robot()
TIME_STEP = int(robot_instance.getBasicTimeStep())

class Liner(rpyc.Service):

    def __init__(self):
        ## Robot
        self.robot = robot_instance
        self.robot_number = int(self.robot.getName().split("_")[1])
        self.port = 3000 + self.robot_number

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

        ## Propiedades
        self.state = st.yellow_line
        self.box_on_top_id = None
        self.change_box_id = False
        self.target_color = None
        self.wait_status = None
        self.store_status = False

        ## Clases auxiliares
        self.move = MoveLiner(self.robot, TIME_STEP)

    def exposed_set_box_id(self, new_id):
        self.box_on_top_id = new_id

    def get_target_color(self):
        return "red"
    
    def exposed_get_store_status(self):
        return self.store_status
    
    def check_store_status(self):
        ## checkear todos los store_status del resto de liners
        return True


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

        if(self.state == st.pick_up_box):
            if(self.box_on_top_id != None):
                self.state = st.turn_store

        if(self.state == st.turn_store):
            if(line_color == "black"):
                self.state = st.move_store

        if(self.state == st.move_store):
            if(line_color == "yellow"):
                self.state = st.store_box

        if(self.state == st.store_box):
            if(self.box_on_top_id == None):
                self.state = st.yellow_line

    def main_loop(self):
        supervisor = rpyc.connect("127.0.0.1", 3000)

        while self.robot.step(TIME_STEP) != -1:
            self.state_changer()

            if(self.state == st.yellow_line):
                self.move.follow_line("yellow")

            if(self.state == st.choose_target):
                if(self.target_color == None):
                    self.target_color = self.get_target_color()

                if(self.target_color == "red"):
                    self.move.turn_right()
                else:
                    self.move.turn_left()

            if(self.state == st.move_zone):
                self.move.follow_line("black")

            if(self.state == st.pick_up_box):
                if(self.wait_status == None):
                    self.wait_status = supervisor.root.load_box(self.robot.getName(), None)

                if(self.wait_status == -1):
                    if(self.move.sleep_robot(5)):
                        self.wait_status = None

            if(self.state == st.turn_store):
                if(self.target_color == "red"):
                        self.move.turn_right()
                else:
                    self.move.turn_left()
            
            if(self.state == st.move_store):
                if(self.move.get_line_color() == "gray" and self.check_store_status() == False):
                    self.move.stop()
                else:
                    self.move.follow_line("black")

            if(self.state == st.store_box):
                if(self.move.get_line_color() != "yellow"):
                    self.change_box_id = True
                    if(self.target_color == "red"):
                        self.move.turn_right()
                    else:
                        self.move.turn_left()
                if(self.move.get_line_color() == "yellow" and self.change_box_id):
                    supervisor.root.store_box("store", self.box_on_top_id)
                    self.box_on_top_id = None
                    self.change_box_id = False

                
                    
liner = Liner()
ThreadedServer(liner, hostname="127.0.0.1", port=liner.port).start()
