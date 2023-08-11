import cv2
from cvzone.HandTrackingModule import HandDetector
import socket
from realsense_depth import *

def getDistance(points,frame, prev_dist = None):
    """Obtain the location of the middle point of the registered hand

    Args:
        points (list): list of points to obtain the middle point from
        frame (cv image): cv frame with info on depth used to locate depth of the desired point

    Returns:
        float: Estimated distance of the middle of the hand 
    """
    
    x = 0
    y = 0
    for point in points:
        x=+ point[0]
        y=+ point[1]
    x = int(x/len(points))
    y = int(y/len(points))

    dist = int((frame[x,y])/10)
    return dist,[x,y],prev_dist
    
def setSocket():
    """Create a UDP Socket conection to transmit data to unity

    Returns:
        socket,tuple: socket port and tuple with ip and port
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #port to send to (ip, port)
    serverPort = ("127.0.0.1", 8661)
    return sk,serverPort

def sendData():
    #Parameters
    height = 1200

    #udp info
    sk, serverAddPort = setSocket()

    #webcam
    #Bootup the camera
    dc = DepthCamera()


    #hand detector
    detector = HandDetector(maxHands=1, detectionCon=0.8)

    prev_dist = None

    while True:
        #get the frame
        ret, depth_frame, color_frame = dc.get_frame()

        #get the hands
        hands, color_frame = detector.findHands(color_frame)

        data = []
        

        #land mark values = (x,y,z, overall depth) * 21 (total number of values we have)
        if hands:
            #get the first hand detected
            hand = hands[0]
            
            #get landmark list
            lmlst = hand["lmList"]
            loc = hand["center"]
            
            #get the estimated distence of the center of the hand from the camera            
            dist = int((depth_frame[loc[1],loc[0]])/1)

            for lm in lmlst:
                #Save the data with the oposite value since unity saves data oposite to open cv
                data.extend([lm[0],height - lm[1],lm[2],dist])

            sk.sendto(str.encode(str(data)), serverAddPort)

            #cv2.circle(color_frame, loc, 4, (255,0,0))
            #cv2.putText(color_frame, "{}cm".format(dist), (loc), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 2)
        cv2.imshow("Image", color_frame)
        key = cv2.waitKey(1)
        if key == 32:
            break

if __name__ == "__main__":
    sendData()