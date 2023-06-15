from dataclasses import dataclass

color_red    = [1,0,0]
color_green  = [0,1,0]
color_blue   = [0,0,1]
color_yellow = [1,1,0]


def zone_colors(box_color):
    if(box_color == color_red): ## Para las cajas rojas
        return color_yellow
    elif(box_color == color_blue):
        return color_green
    
def extract_list_colors(color_object):
        red = int(color_object[0])
        green = int(color_object[1])
        blue = int(color_object[2])
        return [red,green,blue]
    
@dataclass
class TargetInfo:
    id : int
    size : int
    pos_x : int
    pos_y : int