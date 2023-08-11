import cv2

from realsense_depth import *


point = (400,300)

def show_distance(event,x,y,args,params):
    global point
    point = (x,y)

#Bootup the camera
dc = DepthCamera()

#Get the position of the mouse
cv2.namedWindow("Color frame")
cv2.setMouseCallback("Color frame", show_distance)

while True:
    ret, depth_frame, color_frame = dc.get_frame()

    #show distance for a specific point
   
    cv2.circle(color_frame, point, 4, (0,0,255))
    #obtain the distance (y,x)
    distance = depth_frame[point[1],point[0]]
    
    cv2.putText(color_frame, "{}mm".format(distance), (point[0], point[1]), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 2)

    cv2.imshow("Color frame", color_frame)
    
    key =cv2.waitKey(1)
    if key == 32:
        break
