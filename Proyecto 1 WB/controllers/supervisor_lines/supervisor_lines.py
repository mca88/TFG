from controller import Supervisor
from threading import Thread
from rpyc.utils.server import ThreadedServer

import rpyc
import sys
import math

sys.path.insert(1, 'C:\\Users\\Lucas\\Desktop\\TFG\\Proyecto 1 WB\\controllers\\utils')

import utils as ut
import ports as port

TOTAL_BOXES = 4

supervisor = Supervisor()
TIME_STEP = int(supervisor.getBasicTimeStep())

class Supervisor_RPYC(rpyc.Service):

    def __init__(self):
        self.supervisor = supervisor

        ## Lista de cajas
        #self.boxes = self.get_world_boxes()
        self.waiting_boxes = []
        self.ready_boxes = []

        ## Flags para cargar cajas
        self.load_box = False
        self.box_id_to_load = -1
        self.tarjet_robot = None

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def get_world_boxes(self):
        total_boxes = []
        for n in range(1,TOTAL_BOXES+1):
            box_def = f"box_{n}"
            total_boxes.append(self.supervisor.getFromDef(box_def))
        return total_boxes

    def exposed_load_box(self, robot, box_id):
        self.load_box = True
        self.tarjet_robot = robot
        self.box_id_to_load = box_id

    def load_box_robot(self):
        robot_pos = self.supervisor.getFromDef(self.tarjet_robot).getField('translation').getSFVec3f()
        robot_rot = self.supervisor.getFromDef(self.tarjet_robot).getField('rotation').getSFRotation()

        box = self.supervisor.getFromId(self.box_id_to_load)

        robot_pos[2] += 0.08
        box.getField('translation').setSFVec3f(robot_pos)
        box.getField('rotation').setSFRotation(robot_rot)
        #box.getField('recognitionColors').removeMF(0)

    def main_loop(self):
        while self.supervisor.step(TIME_STEP) != -1:
            if(self.load_box):
                self.load_box_robot()
                self.load_box = False


instance = Supervisor_RPYC()
ThreadedServer(instance, hostname="127.0.0.1", port=port.SUPERVISOR_PORT).start()

