import utils as ut

rotate_speed = 2
move_speed   = 5

class MoveLiner():

    def __init__(self, robot, time_step):
        self.time_step = time_step
        ## SENSORES
        self.sensors = {
            "center"  : robot.getDevice('ds_center'),
            "ir_left"  : robot.getDevice('ir_left'),
            "ir_right"  : robot.getDevice('ir_right')
        }
        [s.enable(time_step) for s in self.sensors.values()]
        self.maxRange = self.sensors['center'].getMaxValue()

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
        self.turn = None

    def constant_timer(self,steps):
        return int((steps*8) / self.time_step)
    
    def sleep_robot(self, segundos):
        if(self.counter >= segundos):
            self.counter = 0
            return True
        else:
            self.counter += self.time_step/1000
            self.stop()
            return False
        
    def small_turn(self, direction):
        if(self.counter >= 0.15):
            self.counter = 0
            self.turn = None
        else:
            self.counter += self.time_step/1000
            direction()

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
        
    def get_ir_colors(self):
        left  = int(self.sensors['ir_left'].value)
        right = int(self.sensors['ir_right'].value)

        # print(f"{left}, {right}")
        
        left_color  = ut.value_to_color(left)
        right_color = ut.value_to_color(right)

        return [left_color, right_color]
    
    def get_line_color(self):
        ir_colors = self.get_ir_colors()
        if(ir_colors[0] == ir_colors[1] and ir_colors[0] != "???"):
            return ir_colors[0]
        else:
            return None
    
    def follow_line(self, color):
        ds_value = int(self.sensors['center'].value)
        if(ds_value != self.maxRange):
            self.stop()
            return

        ir_colors = self.get_ir_colors()

        l_color = ir_colors[0]
        r_color = ir_colors[1]

        centrado = l_color == color and r_color == color
        fallo_iz = l_color != color and r_color == color
        fallo_de = l_color == color and r_color != color
        fallo = l_color != color and r_color!= color

        if(centrado):
            self.move_forward()
        elif(fallo_iz):
            self.turn_right()
        elif(fallo_de):
            self.turn_left()
        elif(fallo):
            self.move_forward()

        if(self.turn != None):
            self.small_turn(self.turn)