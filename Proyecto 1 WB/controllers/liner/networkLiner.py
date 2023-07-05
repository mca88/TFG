import rpyc
from coordinator import Coordinator

num_robots = 6
IP = "127.0.0.1"
class NetworkLiner:

    exposed_coordinator = None

    def __init__(self, name):
        self.name = name 
        self.robot_number = int(name.split("_")[1])
        self.port = 3000 + self.robot_number
        self.coordinator_port = 3005
        if(self.name == "robot_5"):
            NetworkLiner.exposed_coordinator = Coordinator(False)

        self.supervisor = None

        self.neighbor_port = self.port + 1
        if(self.neighbor_port == 3007):
            self.neighbor_port = 3001

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
            try:
                robot_conn = rpyc.connect(IP, robot_port)
            except:
                continue
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
            try:
                coordinator_conn = rpyc.connect(IP, self.coordinator_port)
                coordinator_answer = coordinator_conn.root.get_net().coordinator.check_color_amout()
                coordinator_conn.close()
            except:
                print(f"El robot {self.name} ha detectado que el coordinador está caído y va a iniciar una elección")
                self.start_coordinator_election()
                return "blue"
            
            return coordinator_answer
        
    def check_store_status(self):
        for n in range(4,num_robots+1):
            robot_port = n+3000
            if(robot_port == self.port):
                continue
            try:
                robot_conn = rpyc.connect(IP, robot_port)
            except:
                continue
            if(robot_conn.root.robot_type == "liner"):
                if(robot_conn.root.exposed_store_status):
                    robot_conn.close()
                    return False
            robot_conn.close()
        return True
        
    ## FUNCIONES COORDINADOR

    def substract_box_ammount(self, color):
        try:
            coordinator_conn = rpyc.connect(IP, self.coordinator_port)
            coordinator_conn.root.get_net().coordinator.substract_amount(color)
            coordinator_conn.close()
        except Exception:
            print(f"El robot {self.name} ha detectado que el coordinador está caído y va a iniciar una elección")
            self.coordinator_port = -1
            self.start_coordinator_election()
            # while(self.coordinator_port == -1):
            #     pass

            # self.substract_box_ammount(color)

    def start_coordinator_election(self):
        election_msg = self.port
        self.send_msg_neighbor(election_msg)

    def send_msg_neighbor(self, msg):
        print(f"Soy {self.name} y voy a enviar mensaje a mi vecino")
        try:
            neighbor = rpyc.connect(IP, self.neighbor_port)
            neighbor.root.get_net().get_election_message(msg)
            neighbor.close()
        except:
            print(f"El robot {self.neighbor_port-3000} está caído, intentando con {self.neighbor_port-3000+1}")
            neighbor = rpyc.connect(IP, self.neighbor_port + 1)
            neighbor.root.get_net().get_election_message(msg)
            neighbor.close()

    def send_new_coordinator(self, new_coordinator):
        try:
            neighbor = rpyc.connect(IP, self.neighbor_port)
            neighbor.root.get_net().new_coordinator(new_coordinator)
            neighbor.close()
        except:
            print(f"El robot {self.neighbor_port-3000} está caído, intentando con {self.neighbor_port-3000+1}")
            neighbor = rpyc.connect(IP, self.neighbor_port + 1)
            neighbor.root.get_net().new_coordinator(new_coordinator)
            neighbor.close()
            
    def exposed_get_election_message(self, max_port):
        print(f"Soy {self.name} y recibo {max_port}")
        if(max_port > self.port):
            election_msg = max_port
        elif(max_port < self.port):
            election_msg = self.port

        if(max_port == self.port):
            NetworkLiner.exposed_coordinator = Coordinator(True)
            self.coordinator_port = self.port
            self.send_new_coordinator(self.port)
        else:
            self.send_msg_neighbor(election_msg)

    def exposed_new_coordinator(self, new_coordinator):
        print(f"Soy {self.name} y mi nuevo coordinador es {new_coordinator}")
        if(self.port != new_coordinator):
            self.coordinator_port = new_coordinator
            self.send_new_coordinator(new_coordinator)
                

            


    