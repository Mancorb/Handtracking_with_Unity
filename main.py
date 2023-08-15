import pyrealsense2 as rs
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector
import socket
import threading

class DepthCamera:
    def __init__(self):
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)



        # Start streaming
        self.pipeline.start(config)

    def get_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        if not depth_frame or not color_frame:
            return False, None, None
        return True, depth_image, color_image

    def release(self):
        self.pipeline.stop()

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

def sendData(hand,sk,depth_frame,height,SAP):
    data = []
    #get landmark list
    lmlst = hand["lmList"]
    loc = hand["center"]
    
    #get the estimated distence of the center of the hand from the camera            
    dist = int((depth_frame[loc[1],loc[0]])/1)
    
    for lm in lmlst:
        #Save the data with the oposite value since unity saves data oposite to open cv
        data.extend([lm[0],height - lm[1],lm[2],dist])

    sk.sendto(str.encode(str(data)), SAP)
    #print(f"-----\nsent: {data}\nto:{SAP}")

def main(n):
    #Parameters
    height = 1200

    #Obtain list of sockets and server add ports
    sockets,saps = socketList(n)

    #webcam
    dc = DepthCamera()

    #list of threads
    threads = []

    #hand detector
    detector = HandDetector(maxHands=n, detectionCon=0.8)

    while True:
        #get the frame
        ret, depth_frame, color_frame = dc.get_frame()

        #get the hands
        hands, color_frame = detector.findHands(color_frame)
        

        #land mark values = (x,y,z) * 21 (total number of points we have per hand)
        if hands:
            for i in range(len(hands)):
                t = threading.Thread(target=sendData, args=(hands[i],sockets[i],depth_frame,height,saps[i]))
                t.start()
                threads.append(t)
            #cv2.circle(color_frame, loc, 4, (255,0,0))
            #cv2.putText(color_frame, "{}cm".format(dist), (loc), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 2)

        for t in threads:
            t.join()
        cv2.imshow("Image", color_frame)
        key = cv2.waitKey(1)

        if key == 32:   
            break

if __name__ == "__main__":
    main(3)