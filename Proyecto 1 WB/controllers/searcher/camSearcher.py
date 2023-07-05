from utils import TargetInfo
import utils as color

cam_margin = 30

class CamSearcher():

    def __init__(self, robot, time_step):
        ## CÁMARA
        self.camera = robot.getDevice('camera')
        self.camera.enable(time_step)
        self.camera.recognitionEnable(time_step)

        self.cam_left_margin = self.camera.getHeight()/2 - cam_margin
        self.cam_right_margin = self.camera.getHeight()/2 + cam_margin
        self.cam_size = self.camera.getWidth() * self.camera.getHeight()

    def get_camera_target(self, target_color) -> TargetInfo:
        camera_objects = self.camera.getRecognitionObjects()
        if(len(camera_objects) == 0): return None

        closest_id = -1
        max_size = 0
        for co in camera_objects:
            co_color = color.extract_list_colors(co.getColors())
            if(co_color == target_color): 
                size2D = co.getSizeOnImage()
                size = size2D[0] * size2D[1]

                if(size > max_size):
                    closest_id = co.getId()
                    max_size = size
                    x = co.getPositionOnImage()[0]
                    y = co.getPositionOnImage()[1]

        if(closest_id != -1):
            return TargetInfo(closest_id, max_size, x, y)
        else:
            return None
        
    def get_robot_ahead(self):
        camera_objects = self.camera.getRecognitionObjects()

        for co in camera_objects:
            co_model = co.getModel()
            if(co_model == "robot"):
                size2D = co.getSizeOnImage()
                size = size2D[0] * size2D[1]
                if(size >= self.cam_size*0.2):
                    return True
        return  False
        
    def target_reached(self, target : TargetInfo, percentage):
        condition = (target.size >= self.cam_size*percentage)
        return (condition)
    
    def update_target(self, target : TargetInfo):
        for co in self.camera.getRecognitionObjects():
            if(co.getId() == target.id):
                size2D = co.getSizeOnImage()
                size = size2D[0] * size2D[1]

                target.size = size
                target.pos_x = co.getPositionOnImage()[0]
                target.pos_y = co.getPositionOnImage()[1]

                return True
        return False