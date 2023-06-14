import random
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
        self.target_robot = None

        ## Flags para almacenar cajas
        self.store_box = False
        self.box_id_to_store = -1
        self.target_zone_id = - 1

        ## Hilo bucle principal
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def get_world_boxes(self):
        total_boxes = []
        for n in range(1,TOTAL_BOXES+1):
            box_def = f"box_{n}"
            box = self.supervisor.getFromDef(box_def)
            if(box.getField('recognitionColors').value == None):
                print(f"La caja {n} no tiene recognition")

            total_boxes.append(box)
        return total_boxes

    def exposed_load_box(self, robot, box_id):
        self.load_box = True
        self.target_robot = robot
        self.box_id_to_load = box_id

    def exposed_store_box(self, zone_id, box_id):
        self.store_box = True
        self.box_id_to_store = box_id
        self.target_zone_id = zone_id

    def load_box_robot(self):
        robot_pos = self.supervisor.getFromDef(self.target_robot).getField('translation').getSFVec3f()
        robot_rot = self.supervisor.getFromDef(self.target_robot).getField('rotation').getSFRotation()

        box = self.supervisor.getFromId(self.box_id_to_load)

        robot_pos[2] += 0.08
        box.getField('translation').setSFVec3f(robot_pos)
        box.getField('rotation').setSFRotation(robot_rot)
        box.getField('recognitionColors').removeMF(0)

    def store_box_zone(self):
        box_to_store = self.supervisor.getFromId(self.box_id_to_store)
        store_zore   = self.supervisor.getFromId(self.target_zone_id).getField('translation').getSFVec3f() 
        while True:
            x = random.uniform(-0.2, 0.2)
            y = random.uniform(-0.2, 0.2)
            if not (-0.07 <= x <= 0.07 and -0.07 <= y <= 0.07):
                break
        
        store_zore[0] += x
        store_zore[1] += y
        store_zore[2] = 0.05

        self.waiting_boxes.append(box_to_store)
        box_to_store.getField('translation').setSFVec3f(store_zore)
        
    def main_loop(self):
        while self.supervisor.step(TIME_STEP) != -1:
            if(self.load_box):
                self.load_box_robot()
                self.load_box = False

            if(self.store_box):
                self.store_box_zone()
                self.store_box = False

instance = Supervisor_RPYC()
ThreadedServer(instance, hostname="127.0.0.1", port=port.SUPERVISOR_PORT).start()

