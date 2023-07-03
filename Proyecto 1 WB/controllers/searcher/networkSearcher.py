import rpyc
import utils as color
num_robots = 6
IP = "127.0.0.1"
class NetworkSearcher:
    def __init__(self, name):
        self.name = name 
        self.robot_number = int(name.split("_")[1])
        self.port = 3000 + self.robot_number
        self.coordinator_port = 3005

        self.supervisor = None

    ## FUNCIONES SUPERVISOR

    def conn_supervisor(self):
        self.supervisor = rpyc.connect(IP, 3000)

    def load_box_on_robot(self, box_id):
        if(self.supervisor == None): self.conn_supervisor()

        self.supervisor.root.load_box(self.name, box_id)

    def store_box_on_zone(self, zone_id, box_id, box_color):
        if(self.supervisor == None): self.conn_supervisor()

        self.supervisor.root.store_box(zone_id, box_id, box_color)

   
    ## FUNCIONES SEARCHER
    def get_target_color(self):
        blue = 0
        red = 0

        for n in range(1, num_robots+1):
            robot_port = n+3000
            if(robot_port == self.port): continue
            try:
                robot_conn = rpyc.connect(IP, robot_port)
            except:
                return None
            
            if(robot_conn.root.robot_type == "searcher"):
                target_color = robot_conn.root.exposed_get_color()
                if(target_color == "red"):
                    red += 1
                if(target_color == "blue"):
                    blue += 1

        if(red < blue):
            return "red"
        elif(blue < red):
            return "blue"
        else:
            return None
    
     ## FUNCIONES COORDINADOR
    def add_box_ammount(self, color):
        coordinator_conn = rpyc.connect(IP, self.coordinator_port)
        coordinator_conn.root.coordinator.add_amount(color)
        coordinator_conn.close()

            

