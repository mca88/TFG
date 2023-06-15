from utils import TargetInfo

rotate_speed = 2
move_speed   = 5
ds_limit = 15

class MoveSearcher():

    def __init__(self, robot, time_step):
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

    def avoid_obstacles(self):
        print(self.reposition)
        center   = self.sensors['center'].getValue()
        left_1   = self.sensors['left_1'].getValue() < self.maxRange
        left_2   = self.sensors['left_2'].getValue() < self.maxRange
        right_1  = self.sensors['right_1'].getValue() < self.maxRange
        right_2  = self.sensors['right_2'].getValue() < self.maxRange

        if(left_1 or left_2):
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

    def move_to_target(self, target : TargetInfo, left_margin, right_margin):
        avoid = self.avoid_obstacles()
        if(avoid): return

        if(target.pos_x < left_margin):
            self.turn_left()
        elif(target.pos_x > right_margin):
            self.turn_right()
        else:
            self.move_forward()

