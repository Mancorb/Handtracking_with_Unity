import pyrealsense2 as rs
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector
import socket
import threading

"""
THIS CODE IS USED TO ONLY END BASSIC DATA TO THE UNITY PROJECT 
"""


class DepthCamera:
    def __init__(self):
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)



        # Start streaming
        self.pipeline.start(config)

    def get_frame(self):
        """Obtain the frames from the camara's perspective.
        Returns:
            frame: depth perspective and color image perspective
        """
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        if not depth_frame or not color_frame:
            return False, None, None
        return True, depth_image, color_image

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

def socketList(n):
    """Create n ammount of UDP sockets

    Args:
        n (int): number of sockets to create

    Returns:
        list tuple: socket and port lists
    """
    #List of udp connections
    SKs =[]
    SAPs = []
    #Assign each a different port to comunicate to
    for i in range(n):
        sk, serverAddPort = setSocket(5001+i)
        SKs.append(sk)
        SAPs.append(serverAddPort)
    return SKs,SAPs

def setSocket(port):
    """Create a UDP Socket conection to transmit data to unity

    Returns:
        socket,tuple: socket port and tuple with ip and port
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #port to send to (ip, port)
    serverPort = ("127.0.0.1", port)
    return sk,serverPort

def sendData(hand,sk,depth_frame,SAP):
    """Send location information of the corresponding port

    Args:
        hand (list): list of data collected by the cv2 handtracking algorithim of one hand
        sk (socket): corresponding UDP socket to send info to UNITY
        depth_frame (frame): single fram with depth info from the camera
        height (int): hight of the frame to analize
        SAP (socket): socket's corresponding port
    """
    height = 1200 #Height used to invert the Y axis for unity
    data = [] #List to store the hand points and depth information
    #Get landmark list
    lmlst = hand["lmList"] #List of hand landmarks
    loc = hand["center"] #Obtain the location of the center of the hand
    
    if loc[1] > 480:
        loc[1] = 479
    if loc[0] >479:
        loc[0]=479

    dist = int((depth_frame[loc[1],loc[0]])/1) #Get the estimated distence of the center of the hand from the camera            
    
    for lm in lmlst:
        data.extend([lm[0],height - lm[1],lm[2],dist]) #Save the data with the oposite value since unity saves data oposite to open cv

    sk.sendto(str.encode(str(data)), SAP)

def main(n,image=None):
    sockets,saps = socketList(n) #Obtain list of sockets and server add ports

    dc = DepthCamera() #webcam access object

    threads = []#list of threads for each hand

    detector = HandDetector(maxHands=n, detectionCon=0.8) #Hand detector
    print("Bootup complete, looking for hands...")

    while True:
        ret, depth_frame, color_frame = dc.get_frame() #get the frame objects
        
        hands, color_frame = detector.findHands(color_frame) #get the hands info list

        print(f"\rTracking {len(hands)}, hands.", end="")
        #land mark values = (x,y,z) * 21 (total number of points we have per hand)
        if hands:
            for i in range(len(hands)):
                #For each hand detected send the data with a socket from the list.
                t = threading.Thread(target=sendData, args=(hands[i],sockets[i],depth_frame,saps[i]))
                t.start()
                threads.append(t)

        for t in threads: t.join() #Join all the threads

        if image: cv2.imshow("Image", color_frame) #show the current image of the camera

        key = cv2.waitKey(1)
        if key == 32: break #close program if SPACEBAR is pressed
    print("\nProcess aborted...")

if __name__ == "__main__":
    main(2,False)
    print("Ending program")