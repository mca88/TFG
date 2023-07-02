import random
from controller import Supervisor
from threading import Thread
from rpyc.utils.server import ThreadedServer

import rpyc

TOTAL_BOXES = 20

supervisor = Supervisor()
TIME_STEP = int(supervisor.getBasicTimeStep())

class Supervisor_RPYC(rpyc.Service):

    def __init__(self):
        self.supervisor = supervisor

        ## Lista de cajas
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

        if(box_id == None and len(self.waiting_boxes) == 0): 
            return -1
        
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

        if(self.box_id_to_load != None):
            box = self.supervisor.getFromId(self.box_id_to_load)
            box.getField('recognitionColors').removeMF(0)
        else:
            box = self.waiting_boxes.pop()
            liner = rpyc.connect("127.0.0.1", 3000 + int(self.target_robot.split("_")[1]))
            liner.root.set_box_id(box.getId())
            liner.close()


        robot_pos[2] += 0.08
        box.getField('translation').setSFVec3f(robot_pos)
        box.getField('rotation').setSFRotation(robot_rot)
        
    def store_box_zone(self):
        box_to_store = self.supervisor.getFromId(self.box_id_to_store)

        if(self.target_zone_id == "store"):
            store_zore   = self.supervisor.getFromDef("store").getField('translation').getSFVec3f()
            rot_zone     = self.supervisor.getFromDef("store").getField('rotation').getSFRotation()
            self.ready_boxes.insert(0, box_to_store)

            x = random.uniform(-0.43, 0.43)
            y = random.uniform(-0.3725, 0.3725)

        else:
            store_zore   = self.supervisor.getFromId(self.target_zone_id).getField('translation').getSFVec3f()
            rot_zone     = self.supervisor.getFromId(self.target_zone_id).getField('rotation').getSFRotation()
            self.waiting_boxes.insert(0, box_to_store)

            x = random.uniform(-0.25, 0.25)
            y = random.uniform(-0.25, 0.25)

        store_zore[0] += x
        store_zore[1] += y
        store_zore[2] = 0.05

        
        box_to_store.getField('translation').setSFVec3f(store_zore)
        box_to_store.getField('rotation').setSFRotation(rot_zone)
        
    def main_loop(self):
        while self.supervisor.step(TIME_STEP) != -1:
            print(self.waiting_boxes)
            if(self.load_box):
                self.load_box_robot()
                self.load_box = False

            if(self.store_box):
                self.store_box_zone()
                self.store_box = False

instance = Supervisor_RPYC()
ThreadedServer(instance, hostname="127.0.0.1", port=3000).start()

