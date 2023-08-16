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

def saveData(hand,depth_frame,name,n):
    """Record hand point location and overall distance from camera to a specific file in a corresponding file.
    As soon as the loop reaches the limit the previous file with the same 'n' will be replaced with new data to not overwhelm the storage.

    Args:
        hand (list): list of info of the selected hand
        depth_frame (frame): image frame of camera depth perseption
        name (string): name of the Folder to safe the file to
        n (int): iteration of the file
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
    
    location = f"./Hand_{name}/[{n}].txt" #Hand_A/[0]

    with open(location,"w") as file: #save the info in the corresponding file
        for lm in lmlst:
            file.write(f"{lm[0]},{height - lm[1]},{lm[2]}\n")
            file.write(str(dist))

def main(n,image=None,):
    dc = DepthCamera() #webcam access object
    threads = []#list of threads for each hand
    detector = HandDetector(maxHands=n, detectionCon=0.8) #Hand detector object
    counter = 0 #File counter
    FILES=["A","B","C","D"]#Folder names
    LIMIT = 20

    print("Bootup complete, looking for hands...")

    while True:
        ret, depth_frame, color_frame = dc.get_frame() #get the frame objects
        hands, color_frame = detector.findHands(color_frame) #get the hands info list
        print(f"\rTracking {len(hands)}, hands.", end="")

        #land mark values = (x,y,z) * 21 (total number of points we have per hand)
        if hands:
            for i in range(len(hands)):
                #For each hand detected store the data
                t = threading.Thread(target=saveData, args=(hands[i],depth_frame,
                                                            FILES[i],counter))
                t.start()
                threads.append(t)

        for t in threads: t.join() #Join all the threads
        
        counter +=1
        #Reset counter when it reaches the limit to start replaceing old files
        if counter > LIMIT: counter = 0
        #Show the current image of the camera
        if image: cv2.imshow("Image", color_frame)

        key = cv2.waitKey(1)
        if key == 32: break #Close program if SPACEBAR is pressed
    print("\nProcess aborted...")

if __name__ == "__main__":
    main(2,True)
    print("Ending program")