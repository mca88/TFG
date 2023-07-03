import rpyc
num_robots = 6
IP = "127.0.0.1"
class NetworkLiner:
    def __init__(self, name):
        self.name = name 
        self.robot_number = int(name.split("_")[1])
        self.port = 3000 + self.robot_number
        self.coordinator_port = 3005

        self.supervisor = None

    ## FUNCIONES SUPERVISOR
    def conn_supervisor(self):
        self.supervisor = rpyc.connect(IP, 3000)
    
    def load_box_on_robot(self, color):
        if(self.supervisor == None):
            self.conn_supervisor()

        status = self.supervisor.root.load_box(self.name, "liner", color)
        return status

    def store_box_on_zone(self, box_id):
        if(self.supervisor == None): self.conn_supervisor()

        self.supervisor.root.store_box("liner", box_id)

    ## FUNCIONES LINER
    def choose_target_color(self):
        blue = 0
        red = 0

        for n in range(4,num_robots+1):
            robot_port = n+3000
            if(robot_port == self.port): continue

            robot_conn = rpyc.connect(IP, robot_port)
            if(robot_conn.root.robot_type == "liner"):
                if(robot_conn.root.target_color == "red"):
                    red += 1
                elif(robot_conn.root.target_color == "blue"):
                    blue += 1
            robot_conn.close()

        if(red < blue):
            return "red"
        elif(blue < red):
            return "blue"
        else:
            coordinator_conn = rpyc.connect(IP, self.coordinator_port)
            coordinator_answer = coordinator_conn.root.coordinator.check_color_amout()
            coordinator_conn.close()
            return coordinator_answer
        
    def check_store_status(self):
        for n in range(4,num_robots+1):
            robot_port = n+3000
            if(robot_port == self.port):
                continue

            robot_conn = rpyc.connect(IP, robot_port)
            if(robot_conn.root.robot_type == "liner"):
                if(robot_conn.root.exposed_store_status):
                    robot_conn.close()
                    return False
            robot_conn.close()
        return True
        
    ## FUNCIONES COORDINADOR

    def substract_box_ammount(self, color):
        coordinator_conn = rpyc.connect(IP, self.coordinator_port)
        coordinator_conn.root.coordinator.substract_amount(color)
        coordinator_conn.close()

    