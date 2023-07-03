from utils import TargetInfo
from camSearcher import CamSearcher

rotate_speed = 2
move_speed   = 5
ds_limit_1 =  20
ds_limit_2 = 16

class MoveSearcher():

    def __init__(self, robot, time_step, cam : CamSearcher):
        self.time_step = time_step
         ## SENSORES
        self.sensors = {
            "left_1"  : robot.getDevice('ds_left_1'),
            "right_1" : robot.getDevice('ds_right_1'),
            "center"  : robot.getDevice('ds_center'),
            "left_2" : robot.getDevice('ds_left_2'),
            "right_2" : robot.getDevice('ds_right_2')
        }
        [s.enable(time_step) for s in self.sensors.values()]
        self.maxRange = self.sensors['left_1'].getMaxValue()

        ## RUEDAS
        w1 = robot.getDevice('wheel1')
        w2 = robot.getDevice('wheel2')
        w3 = robot.getDevice('wheel3')
        w4 = robot.getDevice('wheel4')
        self.wheels = [w1,w2,w3,w4]
        self.lwheels = [w1,w3]
        self.rwheels = [w2,w4]

        for w in self.wheels:
            w.setPosition(float('inf'))
            w.setVelocity(0.0)

        ## PROPIEDADES
        self.counter = 0
        self.reposition = False
        self.last_obstacle = "left"
        self.search_state = 1

        ## Aux camara
        self.cam = cam
        self.left_margin = cam.cam_left_margin
        self.right_margin = cam.cam_right_margin

    def constant_timer(self,steps):
        return int((steps*8) / self.time_step)

    def turn_right(self):
        [w.setVelocity(rotate_speed) for w in self.lwheels]
        [w.setVelocity(-rotate_speed) for w in self.rwheels]
    
    def turn_left(self):
        [w.setVelocity(rotate_speed) for w in self.rwheels]
        [w.setVelocity(-rotate_speed) for w in self.lwheels]

    def move_forward(self):
        [w.setVelocity(move_speed) for w in self.wheels]

    def stop(self):
        [w.setVelocity(0) for w in self.wheels]

    def small_forward(self):
        if(self.counter == self.constant_timer(200)):
            self.counter = 0
            return True
        else:
            self.move_forward()
            self.counter += 1
            return False

    def full_rotation(self, rotation_dir):
        if(self.counter == self.constant_timer(890)):
            self.counter = 0
            return True
        else:
            if(rotation_dir == "left"):
                self.turn_left()
            else:
                self.turn_right()
            self.counter += 1
            return False
        
    def reposition_forward(self):
        if(self.counter == self.constant_timer(200)):
            self.counter = 0
            self.reposition = False
        else:
            self.counter += 1
            self.move_forward()

    def get_robot_ahead(self):
        camera_objects = self.cam.camera.getRecognitionObjects()

        for co in camera_objects:
            co_model = co.getModel()
            if(co_model == "robot"):
                size2D = co.getSizeOnImage()
                size = size2D[0] * size2D[1]
                if(size >= self.cam.cam_size*0.2):
                    return True
        return  False

    def avoid_obstacles(self):
        if(self.get_robot_ahead()):
            self.stop()
            return True
        
        center_v  = int(self.sensors['center'].getValue())
        left_1_v  = int(self.sensors['left_1'].getValue())
        left_2_v  = int(self.sensors['left_2'].getValue())
        right_1_v = int(self.sensors['right_1'].getValue()) 
        right_2_v = int(self.sensors['right_2'].getValue())

        center  = center_v < self.maxRange
        left_1  = left_1_v < ds_limit_1
        left_2  = left_2_v < ds_limit_2
        right_1 = right_1_v < ds_limit_1
        right_2 = right_2_v < ds_limit_2

        if(False):
            print("----------------------")
            print(f"LEFT 2 : {left_2_v}")
            print(f"LEFT 1 : {left_1_v}")
            print(f"CENTER : {center_v}")
            print(f"RIGHT 1: {right_1_v}")
            print(f"RIGHT 2: {right_2_v}")
        

        if((left_2 and right_2) and (not center)):
           self.move_forward()
           return True

        elif(left_1 or left_2):
            self.reposition = True
            self.last_obstacle = "left"
            self.counter = 0
            self.turn_right()
            return True

        elif(right_1 or right_2):
            self.reposition = True
            self.last_obstacle = "right"
            self.counter = 0
            self.turn_left()
            return True

        elif(self.reposition):
            self.reposition_forward()
            return True
        
    def move_to_search(self):
        avoid = self.avoid_obstacles()
        if(avoid): return 

        if(self.search_state == 1):
            if(self.full_rotation(self.last_obstacle)):
                self.search_state = 2
        else:
            if(self.small_forward()):
                self.search_state = 1
                return True

    def move_to_target(self, target : TargetInfo):
        avoid = self.avoid_obstacles()
        if(avoid): return

        if(target.pos_x < self.left_margin):
            self.turn_left()
        elif(target.pos_x > self.right_margin):
            self.turn_right()
        else:
            self.move_forward()

